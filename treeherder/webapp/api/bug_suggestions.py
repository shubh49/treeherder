# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

from rest_framework import viewsets
from rest_framework.response import Response
from treeherder.webapp.api.utils import (UrlQueryFilter, with_jobs,
                                         oauth_required)


class BugSuggestionsViewSet(viewsets.ViewSet):

    """
    This viewset is responsible for the bug_suggestions endpoint.

    This will take a list of error lines and determine which bugs to suggest
    for each.
    """

    def list(self, request, project, jm):
        """
        return a list of job artifacts
        """
        # @todo: remove after old data expires from this change on 3/5/2015
        qparams = request.QUERY_PARAMS.copy()
        name = qparams.get('name', None)
        if name and name == 'text_log_summary':
            qparams['name__in'] = 'text_log_summary,Structured Log'
            del(qparams['name'])
        # end remove block

        # @todo: change ``qparams`` back to ``request.QUERY_PARAMS``
        filter = UrlQueryFilter(qparams)

        offset = filter.pop("offset", 0)
        count = min(int(filter.pop("count", 10)), 1000)

        objs = jm.get_job_artifact_list(offset, count, filter.conditions)
        return Response(objs)
