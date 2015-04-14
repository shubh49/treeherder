import logging
import zlib

from treeherder.etl.perf_data_adapters import PerformanceDataAdapter

logger = logging.getLogger(__name__)


class ArtifactModel(object):

    def __init__(self, jobs_model):
        self.jm = jobs_model


    def load_job_artifacts(self, artifact_data, job_id_lookup, add_bug_suggestions=False):
        """
        Determine what type of artifacts are contained in artifact_data and
        store a list of job artifacts substituting job_guid with job_id. All
        of the datums in artifact_data need to be one of the three
        different tasty "flavors" described below.

        artifact_placeholders:

            Comes in through the web service as the "artifacts" property
            in a job in a job collection
            (https://github.com/mozilla/treeherder-client#job-collection)

            A list of lists
            [
                [job_guid, name, artifact_type, blob, job_guid, name]
            ]

        job_artifact_collection:

            Comes in  through the web service as an artifact collection.
            (https://github.com/mozilla/treeherder-client#artifact-collection)

            A list of job artifacts:
            [
                {
                    'type': 'json',
                    'name': 'my-artifact-name',
                    # blob can be any kind of structured data
                    'blob': { 'stuff': [1, 2, 3, 4, 5] },
                    'job_guid': 'd22c74d4aa6d2a1dcba96d95dccbd5fdca70cf33'
                }
            ]

        performance_artifact:

            Same structure as a job_artifact_collection but the blob contains
            a specialized data structure designed for performance data.

        If ``add_bug_suggestions`` is True, then check each artifact for a list
        of errors and attempt to find bug suggestions for them.  Then add those
        to the artifact.
        """
        artifact_placeholders_list = []
        job_artifact_list = []

        performance_artifact_list = []
        performance_artifact_job_id_list = []

        for index, artifact in enumerate(artifact_data):

            # Determine what type of artifact we have received
            if artifact:

                job_id = None
                job_guid = None

                if isinstance(artifact, list):

                    job_guid = artifact[0]
                    job_id = job_id_lookup.get(job_guid, {}).get('id', None)

                    self._adapt_job_artifact_placeholders(
                        artifact, artifact_placeholders_list, job_id)

                else:
                    artifact_name = artifact['name']
                    job_guid = artifact.get('job_guid', None)
                    job_id = job_id_lookup.get(
                        artifact['job_guid'], {}
                    ).get('id', None)

                    if artifact_name in PerformanceDataAdapter.performance_types:
                        self._adapt_performance_artifact_collection(
                            artifact, performance_artifact_list,
                            performance_artifact_job_id_list, job_id)
                    else:
                        self._adapt_job_artifact_collection(
                            artifact, job_artifact_list, job_id)

                if not job_id:
                    logger.error(
                        ('load_job_artifacts: No job_id for '
                         '{0} job_guid {1}'.format(self.jm.project, job_guid)))

            else:
                logger.error(
                    ('load_job_artifacts: artifact not '
                     'defined for {0}'.format(self.jm.project)))

        # Store the various artifact types if we collected them
        if artifact_placeholders_list:
            self.jm.store_job_artifact(artifact_placeholders_list)

        if job_artifact_list:
            self.jm.store_job_artifact(job_artifact_list)

        if performance_artifact_list and performance_artifact_job_id_list:
            self.jm.store_performance_artifact(
                performance_artifact_job_id_list, performance_artifact_list)

    def _adapt_job_artifact_placeholders(
            self, artifact, artifact_placeholders_list, job_id):

        if job_id:
            # Replace job_guid with id in artifact data
            artifact[0] = job_id
            artifact[4] = job_id

            artifact_placeholders_list.append(artifact)

    def _adapt_job_artifact_collection(
            self, artifact, artifact_data, job_id):

        if job_id:
            artifact_data.append((
                job_id,
                artifact['name'],
                artifact['type'],
                zlib.compress(artifact['blob']),
                job_id,
                artifact['name'],
            ))

    def _adapt_performance_artifact_collection(
            self, artifact, artifact_data, job_id_list, job_id):

        if job_id:
            job_id_list.append(job_id)
            artifact_data.append(artifact)

