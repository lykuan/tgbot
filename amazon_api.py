import requests
from paapi5_python_sdk.api.default_api import DefaultApi
from paapi5_python_sdk.get_items_request import GetItemsRequest
from paapi5_python_sdk.get_items_resource import GetItemsResource
from paapi5_python_sdk.partner_type import PartnerType
from paapi5_python_sdk.rest import ApiException
from constants import *
import re
import os
import json

class AmazonAPI:
    def __init__(self):
        self.access_key = AMAZON_ACCESS_KEY
        self.secret_key = AMAZON_SECRET_KEY
        self.region = AMAZON_REGION

    def get_product_from_url(self, url):
        print("\n=== Available Resources ===")
        resource_attrs = [
            attr for attr in dir(GetItemsResource) if not attr.startswith("_")
        ]
        print("\n".join(resource_attrs))
        print("\n=== End Resources ===\n")

        get_items_resource = [
            GetItemsResource.ITEMINFO_TITLE,
            GetItemsResource.OFFERS_LISTINGS_PRICE,
            GetItemsResource.IMAGES_PRIMARY_LARGE,
            GetItemsResource.OFFERS_LISTINGS_PROMOTIONS,
            GetItemsResource.OFFERS_LISTINGS_SAVINGBASIS,
            GetItemsResource.OFFERS_LISTINGS_DELIVERYINFO_ISPRIMEELIGIBLE,
            GetItemsResource.OFFERS_LISTINGS_ISBUYBOXWINNER,
        ]

        asin = re.search(r"(?:dp/|product/)([A-Z0-9]{10})", url)
        marketplace_match = re.search(r"https?://(?:www\.)?(amazon\.[^/]+)", url)

        if not asin:
            print("ASIN not found in URL")
            return None

        if not marketplace_match:
            print("Invalid Amazon URL")
            return None

        asin = asin.group(1)
        marketplace_domain = marketplace_match.group(1)  # e.g., amazon.com
        marketplace_url = f"www.{marketplace_domain}"

        partner_tag = PARTNER_TAG
        if not marketplace_domain.endswith("com") and PARTNER_TAG.endswith("-20"):
            print("Warning: Using US partner tag with non-US marketplace may not work")

        print(f"Using marketplace: {marketplace_url}")
        try:
            request = GetItemsRequest(
                partner_tag=partner_tag,
                partner_type=PartnerType.ASSOCIATES,
                marketplace=marketplace_url,
                item_ids=[asin],
                resources=get_items_resource,
            )
        except Exception as e:
            print(f"Error creating request: {e}")
            return None

        try:
            host = f"webservices.{marketplace_domain}"
            print(host, "--host")

            api = DefaultApi(
                access_key=self.access_key,
                secret_key=self.secret_key,
                host=host,
                region=self.region,
            )

            response = api.get_items(request)

            if not response:
                print("No response received")
                return None

            try:
                items_result = getattr(response, "items_result", None)
                if (
                    not items_result
                    or not hasattr(items_result, "items")
                    or not items_result.items
                ):
                    print("No items found in response")
                    return None

                print("\n=== Product Data Structure ===")
                product = items_result.items[0]
                print(
                    "Offers:",
                    dir(product.offers) if hasattr(product, "offers") else "No offers",
                )
                if (
                    hasattr(product, "offers")
                    and product.offers
                    and product.offers.listings
                ):
                    print("Offer listings:", dir(product.offers.listings[0]))
                    print(
                        "Promotions:",
                        product.offers.listings[0].promotions
                        if hasattr(product.offers.listings[0], "promotions")
                        else "No promotions",
                    )
                return product
            except AttributeError as e:
                print(f"Error accessing response data: {e}")
                return None

        except ApiException as e:
            print("Exception when calling DefaultApi->get_items: %s\n" % e)
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
