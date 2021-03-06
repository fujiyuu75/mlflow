import os
import mock
import pytest

from mlflow.store.artifact.artifact_repository_registry import get_artifact_repository
from mlflow.store.artifact.local_artifact_repo import LocalArtifactRepository
from mlflow.store.artifact.dbfs_artifact_repo import DbfsRestArtifactRepository

from mlflow.utils.rest_utils import MlflowHostCreds


@pytest.fixture()
def host_creds_mock():
    with mock.patch('mlflow.store.artifact.dbfs_artifact_repo._get_host_creds_from_default_store') \
            as get_creds_mock:
        get_creds_mock.return_value = lambda: MlflowHostCreds('http://host')
        yield


@mock.patch('mlflow.utils.databricks_utils.is_dbfs_fuse_available')
def test_dbfs_artifact_repo_delegates_to_correct_repo(
        is_dbfs_fuse_available, host_creds_mock):  # pylint: disable=unused-argument
    is_dbfs_fuse_available.return_value = True
    artifact_uri = "dbfs:/databricks/my/absolute/dbfs/path"
    repo = get_artifact_repository(artifact_uri)
    assert isinstance(repo, LocalArtifactRepository)
    assert repo.artifact_dir == os.path.join(
        os.path.sep, "dbfs", "databricks", "my", "absolute", "dbfs", "path")
    with mock.patch.dict(os.environ, {'MLFLOW_ENABLE_DBFS_FUSE_ARTIFACT_REPO': 'false'}):
        fuse_disabled_repo = get_artifact_repository(artifact_uri)
    assert isinstance(fuse_disabled_repo, DbfsRestArtifactRepository)
    assert fuse_disabled_repo.artifact_uri == artifact_uri
    is_dbfs_fuse_available.return_value = False
    rest_repo = get_artifact_repository(artifact_uri)
    assert isinstance(rest_repo, DbfsRestArtifactRepository)
    assert rest_repo.artifact_uri == artifact_uri
