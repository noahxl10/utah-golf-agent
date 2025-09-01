
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
    "Glendale Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "547936f8-0f45-4bea-b557-d15a4de485ad",
                "4984e272-06a5-446a-8e24-8402e3591b7c"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/glendale-golf-course"
        }
    },
    "Rose Park Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "19a5558e-3821-4935-b6bd-0cbc99693d91",
                "f899015b-2109-4028-8640-d670ada581e4"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/rose-park-golf-course"
        }
    },
    "Forest Dale Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "41ea25ca-ffcb-4f14-a86d-de0ef84510e0",
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/forest-dale-golf-course"
        }
    },
    "Nibley Park Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "997cd01f-4ce8-4462-a459-594762efb606"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/nibley-park-golf-course"
        }
    },
    "River Oaks Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "79c03256-be52-4e3d-aba8-9c64df6e12b2",
                "026599af-6569-4b0f-aaf9-aefedc607e3c"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/river-oaks-golf-course-utah"
        }
    },
    "Mountain Dell Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "2c162b65-6803-4bad-9a21-4c1ca88bb242",
                "77dca1a2-edae-47d2-a202-a1e9391cc305",
                "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/mountain-dell-golf-club"  # pattern‐based; needs validation
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
    "Riverbend Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "8ceb87d6-0afb-4361-a633-1b1d3f6e5805",
                "a10735ef-5ac1-4ad1-b5e8-8721c344a1ac"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/riverbend-slco"  # Not located yet
        }
    },
    "South Mountain Golf Course": {
        "provider": "chronogolf",
        "config": {
            "version": "marketplaceV2",
            "course_ids": [
                "bc4c00f2-435a-4f4a-8d0a-c807d5f515f0",
                "9bb16c41-88fe-4f36-a84c-39f74f8aa5f2"
            ],
            "endpoint_env_var": "CHRONOGOLF_V2_ENDPOINT",
            "booking_url": "https://www.chronogolf.com/club/south-mountain-slco"  # Not matched in Utah
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
    "Eaglewood Golf Course": {
        "provider": "custom",
        "config": {
            "endpoint_env_var": "EAGLEWOOD_ENDPOINT",
            "booking_url": "https://app.membersports.com/tee-times/15391/18901/0"
        }
    },
}
