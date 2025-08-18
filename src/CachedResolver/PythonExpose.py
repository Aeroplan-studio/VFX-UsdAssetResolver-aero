import inspect
import logging
import os
from functools import wraps

try:
    from pxr import Ar
except:
    from fnpxr import Ar

# Init logger
logging.basicConfig(format="%(asctime)s %(message)s", datefmt="%Y/%m/%d %I:%M:%S%p")
LOG = logging.getLogger("Python | {file_name}".format(file_name=__name__))
LOG.setLevel(level=logging.INFO)


def log_function_args(func):
    """Decorator to print function call details."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        func_args = inspect.signature(func).bind(*args, **kwargs).arguments
        func_args_str = ", ".join(map("{0[0]} = {0[1]!r}".format, func_args.items()))
        # To enable logging on all methods, re-enable this.
        # LOG.info(f"{func.__module__}.{func.__qualname__} ({func_args_str})")
        return func(*args, **kwargs)

    return wrapper


class UnitTestHelper:
    create_relative_path_identifier_call_counter = 0
    context_initialize_call_counter = 0
    resolve_and_cache_call_counter = 0
    current_directory_path = ""

    @classmethod
    def reset(cls, current_directory_path=""):
        cls.create_relative_path_identifier_call_counter = 0
        cls.context_initialize_call_counter = 0
        cls.resolve_and_cache_call_counter = 0
        cls.current_directory_path = current_directory_path


def TfIsRelativePath(path):
    """Check if the path is not an absolute path,
    by checking if it starts with "/" or "\\" depending on the host
    os path style.
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative path
    """
    if SYSTEM_IS_WINDOWS:
        drive, tail = os.path.splitdrive(path)
        return not path or (path[0] != '/' and path[0] != '\\' and not drive)
    else:
        return not path or path[0] != '/'


def _IsRelativePath(path):
    """Check if the path is not an absolute path,
    by checking if it starts with "/" or "\\"
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative path
    """
    return path and TfIsRelativePath(path)


def _IsFileRelativePath(path):
    """Check if the path is a relative file path
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a relative file path
    """
    return path.startswith("./") or path.startswith("../")


def _IsSearchPath(path):
    """Check if the path is search path resolveable
    Args:
        path(str): The path
    Returns:
        bool: State if the path is a search path resolveable path
    """
    return _IsRelativePath(path) and not _IsFileRelativePath(path)


def _AnchorRelativePath(anchorPath, path):
    """Anchor the relative path by the anchor path.
    Args:
        anchorPath(str): The anchor path
        path(str): The path to anchor
    Returns:
        str: An anchored path
    """
    if (TfIsRelativePath(anchorPath) or not _IsRelativePath(path)):
        return path
    # Ensure we are using forward slashes and not back slashes.
    forwardPath = anchorPath.replace('\\', '/')
    # If anchorPath does not end with a '/', we assume it is specifying
    ## a file, strip off the last component, and anchor the path to that
    ## directory.
    anchoredPath = os.path.join(os.path.dirname(forwardPath), path)
    return os.path.normpath(anchoredPath)


def _ResolveAnchored(anchorPath, path):
    """Anchor the path by the anchor path.
    Args:
        anchorPath(str): The anchor path
        path(str): The path to anchor
    Returns:
        Ar.ResolvedPath: An anchored resolved path
    """
    resolvedPath = path
    if (anchorPath):
        resolvedPath = os.path.join(anchorPath, path)
    return Ar.ResolvedPath(os.path.normpath(resolvedPath)) if os.path.isfile(resolvedPath) else Ar.ResolvedPath()


def _GetMappingPairsFromUsdFile(mappingFilePath):
    """Lookup mapping pairs from the given mapping .usd file.
    Args:
        mappingFilePath(str): The mapping .usd file path
    Returns:
        mappingPairs(dict): A dict of mapping pairs
    """
    if not os.path.isfile(mappingFilePath) or not mappingFilePath.endswith((".usd", ".usdc", ".usda")):
        return {}
    layer = Sdf.Layer.FindOrOpen(mappingFilePath)
    if not layer:
        return {}
    layerMetaData = layer.customLayerData
    mappingPairs = layerMetaData.get(Tokens.mappingPairs)
    if not mappingPairs:
        return {}
    if len(mappingPairs) % 2 != 0:
        return {}
    mappingPairs = dict(zip(mappingPairs[::2], mappingPairs[1::2]))
    return mappingPairs


class Resolver:

    @staticmethod
    @log_function_args
    def CreateRelativePathIdentifier(resolver, anchoredAssetPath, assetPath, anchorAssetPath):
        """Returns an identifier for the asset specified by assetPath and anchor asset path.
        It is very important that the anchoredAssetPath is used as the cache key, as this
        is what is used in C++ to do the cache lookup.

        We have two options how to return relative identifiers:
        - Make it absolute: Simply return the anchoredAssetPath. This means the relative identifier
                            will not be passed through to ResolverContext.ResolveAndCache.
        - Make it non file based: Make sure the remapped identifier does not start with "/", "./" or"../"
                                  by putting some sort of prefix in front of it. The path will then be
                                  passed through to ResolverContext.ResolveAndCache, where you need to re-construct
                                  it to an absolute path of your liking. Make sure you don't use a "<somePrefix>:" syntax,
                                  to avoid mixups with URI based resolvers.

        Args:
            resolver (CachedResolver): The resolver
            anchoredAssetPath (str): The anchored asset path, this has to be used as the cached key.
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): A resolved anchor path.

        Returns:
            str: The identifier.
        """
        LOG.debug("::: Resolver.CreateRelativePathIdentifier | {} | {} | {}".format(anchoredAssetPath, assetPath, anchorAssetPath))
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.create_relative_path_identifier_call_counter += 1
        remappedRelativePathIdentifier = f"relativePath|{assetPath}?{anchorAssetPath}".replace("//", "/")
        resolver.AddCachedRelativePathIdentifierPair(anchoredAssetPath, remappedRelativePathIdentifier)
        return remappedRelativePathIdentifier

    @staticmethod
    @log_function_args
    def _CreateIdentifier(assetPath, anchorAssetPath, serializedContext, serializedFallbackContext):
        """Returns an identifier for the asset specified by assetPath.
        If anchorAssetPath is not empty, it is the resolved asset path
        that assetPath should be anchored to if it is a relative path.
        Args:
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): An resolved anchor path.
            serializedContext (str): The serialized context.
            serializedFallbackContext (str): The serialized fallback context.
        Returns:
            str: The identifier.
        """
        if not assetPath:
            return assetPath
        if not anchorAssetPath:
            return os.path.normpath(assetPath)
        anchoredAssetPath = _AnchorRelativePath(anchorAssetPath.GetPathString(), assetPath)
        if (_IsSearchPath(assetPath) and not Resolver._Resolve(anchoredAssetPath,serializedContext, serializedFallbackContext)):
            return os.path.normpath(assetPath)
        return os.path.normpath(anchoredAssetPath)

    @staticmethod
    @log_function_args
    def _CreateIdentifierForNewAsset(assetPath, anchorAssetPath):
        """Return an identifier for a new asset at the given assetPath.
        This is similar to _CreateIdentifier but is used to create identifiers
        for assets that may not exist yet and are being created.
        Args:
            assetPath (str): An unresolved asset path.
            anchorAssetPath (Ar.ResolvedPath): An resolved anchor path.
        Returns:
            str: The identifier.
        """
        if not assetPath:
            return assetPath
        if _IsRelativePath(assetPath):
            if anchorAssetPath:
                return os.path.normpath(_AnchorRelativePath(anchorAssetPath.GetPathString(), assetPath))
            else:
                return os.path.normpath(assetPath)
        return os.path.normpath(assetPath)

    @staticmethod
    @log_function_args
    def _Resolve(assetPath, serializedContext, serializedFallbackContext):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """
        if not assetPath:
            return Ar.ResolvedPath()
        if _IsRelativePath(assetPath):
            if Resolver._IsContextDependentPath(assetPath):
                for data in [serializedContext, serializedFallbackContext]:
                    if not data:
                        continue
                    try:
                        ctx = json.loads(data)
                    except Exception:
                        print("Failed to extract context, data is not serialized json data: {data}".format(data=data))
                        continue
                    mappingPairs = ctx.get(Tokens.mappingPairs, {})
                    mappedPath = assetPath
                    if mappingPairs:
                        if ctx.get(Tokens.mappingRegexExpression, ""):
                            mappedPath = re.sub(ctx[Tokens.mappingRegexExpression],
                                                ctx.get(Tokens.mappingRegexFormat, ""),
                                                mappedPath)
                    mappedPath = mappingPairs.get(mappedPath, mappedPath)
                    for searchPath in ctx.get(Tokens.searchPaths, []):
                        resolvedPath = _ResolveAnchored(searchPath, mappedPath)
                        if resolvedPath:
                            return resolvedPath
                    # Only try the first valid context.
                    break
        return _ResolveAnchored("", assetPath)

    @staticmethod
    @log_function_args
    def _ResolveForNewAsset(assetPath):
        """Return the resolved path for the given assetPath that may be
        used to create a new asset or an empty ArResolvedPath if such a
        path cannot be computed.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            Ar.ResolvedPath: The resolved path.
        """
        return Ar.ResolvedPath(assetPath if not assetPath else os.path.abspath(os.path.normpath(assetPath)))

    @staticmethod
    @log_function_args
    def _IsContextDependentPath(assetPath):
        """Returns true if assetPath is a context-dependent path, false otherwise.
        Args:
            assetPath (str): An unresolved asset path.
        Returns:
            bool: The context-dependent state.
        """
        return _IsSearchPath(assetPath)

    @staticmethod
    @log_function_args
    def _GetModificationTimestamp(assetPath, resolvedPath):
        """Return an ArTimestamp representing the last time the asset at assetPath was modified.
        Args:
            assetPath (str): An unresolved asset path.
            resolvePath (Ar.ResolvedPath): A resolved path.
        Returns:
            Ar.Timestamp: The timestamp.
        """
        if not os.path.isfile(resolvedPath.GetPathString()):
            return Ar.Timestamp()
        return Ar.Timestamp(os.path.getmtime(resolvedPath.GetPathString()))
    
class ResolverContext:

    @staticmethod
    @log_function_args
    def Initialize(context):
        """Initialize the context. This get's called on default and post mapping file path
        context creation.

        Here you can inject data by batch calling context.AddCachingPair(assetPath, resolvePath),
        this will then populate the internal C++ resolve cache and all resolves calls
        to those assetPaths will not invoke Python and instead use the cache.

        Args:
            context (CachedResolverContext): The active context.
        """
        LOG.debug("::: ResolverContext.Initialize")
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.context_initialize_call_counter += 1
        context.AddCachingPair("shot.usd", "/some/path/to/a/file.usd")
        # context.AddCachingPair("my_test_usd.usd", "D:/tmp/pomogator_alt.usd")
        return

    @staticmethod
    @log_function_args
    def ResolveAndCache(context, assetPath):
        """Return the resolved path for the given assetPath or an empty
        ArResolvedPath if no asset exists at that path.
        Args:
            context (CachedResolverContext): The active context.
            assetPath (str): An unresolved asset path.
        Returns:
            str: The resolved path string. If it points to a non-existent file,
                 it will be resolved to an empty ArResolvedPath internally, but will
                 still count as a cache hit and be stored inside the cachedPairs dict.
        """
        LOG.debug(
            "::: ResolverContext.ResolveAndCache | {} | {}".format(assetPath, context.GetCachingPairs())
        )
        resolved_asset_path=assetPath
        if assetPath == "my_test_usd.usd":
            context.AddCachingPair("my_test_usd.usd", "C:/sm_temp/Fixies5/models/chars/fixies/nolik/usd/nolik.main.usd")
            resolved_asset_path = "C:/sm_temp/Fixies5/models/chars/fixies/nolik/usd/nolik.main.usd"
        path_prefix='aerofile:'
        if assetPath.startswith(path_prefix) :
            root =   'C:/sm_temp'
            resolved_asset_path = assetPath.replace(path_prefix, root)
            context.AddCachingPair(assetPath, resolved_asset_path)
            print (f"resolved_asset_path: {resolved_asset_path}")
        
        print (f"resolved_asset_path: {resolved_asset_path}")
        return resolved_asset_path

        """Implement custom resolve logic and add the resolved path to the cache.
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        # To clear the context cache call:
        context.ClearCachingPairs()
        """
        """The code below is only needed to verify that UnitTests work."""
        UnitTestHelper.resolve_and_cache_call_counter += 1
        resolved_asset_path = "/some/path/to/a/file.usd"
        context.AddCachingPair(assetPath, resolved_asset_path)
        if assetPath == "unittest.usd":
            current_dir_path = UnitTestHelper.current_directory_path
            asset_a_file_path = os.path.join(current_dir_path, "assetA.usd")
            asset_b_file_path = os.path.join(current_dir_path, "assetB.usd")
            context.AddCachingPair("assetA.usd", asset_a_file_path)
            context.AddCachingPair("assetB.usd", asset_b_file_path)
        relative_path_prefix = "relativePath|"
        if assetPath.startswith(relative_path_prefix):
            relative_path, anchor_path = assetPath[len(relative_path_prefix) :].split(
                "?"
            )
            anchor_path = anchor_path[:-1] if anchor_path[-1] == "/" else anchor_path[:anchor_path.rfind("/")]
            resolved_asset_path = os.path.normpath(os.path.join(anchor_path, relative_path))
            context.AddCachingPair(assetPath, resolved_asset_path)
        print (f"resolved_asset_path: {resolved_asset_path}")
        return resolved_asset_path
