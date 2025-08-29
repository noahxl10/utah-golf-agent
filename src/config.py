
courses = {
    "Bonneville Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",
                "caa8142a-4a42-482b-8d35-4239ce26f7b0"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/bonneville-golf-course"
        }
    },
    "Old Mill Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV1",
            "club_id": "14210",
            "course_ids": ["16298"],
            "endpoint_env_var": "CHRONOGOLF_V1_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/old-mill-slco"  # Not located yet
        }
    },
    "Bountiful Ridge Golf Course": {
        "provider": "foreup",
        "config": {
            "version": "v1",
            "access": "public",
            "endpoint_env_var": "FOREUP_ENDPOINT",
            "booking_url": "https://app.foreupsoftware.com/index.php/booking/18950#/teetimes"
            # No booking_url since provider is different
        }
    },
    # "Stonebridge Golf Club": {
    #     "provider": "foreup",
    #     "config": {
    #         "version": "v1",
    #         "access": "private",
    #     }
    # },
    # "The Ridge Golf Club": {
    #     "provider": "foreup",
    #     "config": {
    #         "version": "v1",
    #         "access": "private",
    #     }
    # },
    # "Eaglewood Golf Course": {
    #     "provider": "custom",
    #     "config": {
    #     }
    # },
}
