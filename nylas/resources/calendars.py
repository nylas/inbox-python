from nylas.handler.api_resources import (
    ListableApiResource,
    FindableApiResource,
    CreatableApiResource,
    UpdatableApiResource,
    DestroyableApiResource,
)
from nylas.models.availability import GetAvailabilityResponse, GetAvailabilityRequest
from nylas.models.calendar import Calendar, CreateCalendarRequest, UpdateCalendarRequest
from nylas.models.delete_response import DeleteResponse
from nylas.models.list_response import ListResponse
from nylas.models.response import Response


class Calendars(
    ListableApiResource,
    FindableApiResource,
    CreatableApiResource,
    UpdatableApiResource,
    DestroyableApiResource,
):
    def list(self, identifier: str) -> ListResponse[Calendar]:
        return super(Calendars, self).list(
            path=f"/v3/grants/{identifier}/calendars",
            response_type=Calendar,
        )

    def find(self, identifier: str, calendar_id: str) -> Response[Calendar]:
        return super(Calendars, self).find(
            path=f"/v3/grants/{identifier}/calendars/{calendar_id}",
            response_type=Calendar,
        )

    def create(
        self, identifier: str, request_body: CreateCalendarRequest
    ) -> Response[Calendar]:
        return super(Calendars, self).create(
            path=f"/v3/grants/{identifier}/calendars",
            response_type=Calendar,
            request_body=request_body,
        )

    def update(
        self, identifier: str, calendar_id: str, request_body: UpdateCalendarRequest
    ) -> Response[Calendar]:
        return super(Calendars, self).update(
            path=f"/v3/grants/{identifier}/calendars/{calendar_id}",
            response_type=Calendar,
            request_body=request_body,
        )

    def destroy(self, identifier: str, calendar_id: str) -> DeleteResponse:
        return super(Calendars, self).destroy(
            path=f"/v3/grants/{identifier}/calendars/{calendar_id}"
        )

    def get_availability(
        self, identifier: str, request_body: GetAvailabilityRequest
    ) -> Response[GetAvailabilityResponse]:
        """Get availability for a calendar.

        Args:
            identifier: The grant ID or email account to get availability for.
            request_body: The request body to send to the API.

        Returns:
            Response: The availability response from the API.
        """
        json_response = self._http_client._execute(
            method="POST",
            path=f"/v3/grants/{identifier}/calendar/availability",
            request_body=request_body,
        )

        return Response.from_dict(json_response, GetAvailabilityResponse)
