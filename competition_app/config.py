"""Module defining settings for the 'competition_app' Django app."""
MESSAGE_CREATED_MODIFIED_INCORRECT_ORDER = (
    'The time and date of the modified field must not be later than ' +
    'the time and date of the created field'
)
MESSAGE_COMPETITION_DATES_INCORRECT_ORDER = 'End date must not be set before the start date'
