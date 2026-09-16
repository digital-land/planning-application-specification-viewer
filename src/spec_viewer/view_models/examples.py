"""Curated example navigation; JSON remains in the source repository."""
EXAMPLE_GROUPS = [
    {
        "name": "Submission payloads",
        "examples": [
            {
                "slug": "full",
                "title": "Example full planning application submission",
                "description": "A submission for full planning permission.",
                "source": "application-type/full--ex1001.json",
            },
            {
                "slug": "outline-some",
                "title": "Example outline planning application submission",
                "description": (
                    "A submission for outline planning permission with some "
                    "matters reserved."
                ),
                "source": "application-type/outline-some--ex1002.json",
            },
            {
                "slug": "reserved-matters",
                "title": "Example reserved matters submission",
                "description": "A submission for approval of reserved matters.",
                "source": "application-type/reserved-matters--ex1003.json",
            },
            {
                "slug": "approval-condition",
                "title": "Example approval of conditions submission",
                "description": "A submission seeking approval of conditions.",
                "source": "application-type/approval-condition--ex1004.json",
            },
            {
                "slug": "advertising",
                "title": "Example advertising consent submission",
                "description": "A submission for advertising consent.",
                "source": "application-type/advertising--ex1005.json",
            },
            {
                "slug": "non-material-amendment",
                "title": "Example non-material amendment submission",
                "description": "A submission for a non-material amendment.",
                "source": "application-type/non-material-amendment--ex1006.json",
            },
        ],
        "route": "submission",
    },
    {
        "name": "Planning application records",
        "examples": [
            {
                "slug": "householder-application",
                "title": "Example householder application",
                "description": (
                    "A complete example of the records for a householder "
                    "planning application."
                ),
                "source": (
                    "planning-application-data/householder-application.json"
                ),
            }
        ],
        "route": "planning-application-data",
    },
]
