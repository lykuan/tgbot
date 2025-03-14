def create_product_post(product):
    print(f"{3 * '*'} Creating post {3 * '*'}")

    if not product:
        return "Sorry, couldn't retrieve product information."

    title = product.item_info.title.display_value
    image_url = None
    try:
        if hasattr(product.images.primary, "large") and product.images.primary.large:
            image_url = product.images.primary.large.url
        elif (
            hasattr(product.images.primary, "medium") and product.images.primary.medium
        ):
            image_url = product.images.primary.medium.url
        elif hasattr(product.images, "variants") and product.images.variants:
            if hasattr(product.images.variants[0], "large"):
                image_url = product.images.variants[0].large.url
            elif hasattr(product.images.variants[0], "medium"):
                image_url = product.images.variants[0].medium.url

        if not image_url:
            raise AttributeError("No image URL found")

    except AttributeError as e:
        print(f"Error: Could not get any image URL - {str(e)}")
        return "Sorry, couldn't retrieve product information."

    try:
        price = int(float(product.offers.listings[0].price.amount) * 100) / 100.0
    except (ValueError, AttributeError):
        print("Error: Could not parse price")
        return "Sorry, couldn't retrieve product information."

    product_url = product.detail_page_url

    html = f"🛒 <b>{title}</b>\n\n"
    html += f"💰 <b>${price:,.2f}</b>"

    try:
        if (
            hasattr(product.offers.listings[0].price, "savings")
            and product.offers.listings[0].price.savings
        ):
            savings_info = product.offers.listings[0].price.savings
            if hasattr(savings_info, "amount"):
                savings = int(float(savings_info.amount) * 100) / 100.0
                original_price = price + savings
                savings_text = f" instead of ${original_price:,.2f}"
                if hasattr(savings_info, "percentage"):
                    savings_text += (
                        f" (save ${savings:,.2f} | {savings_info.percentage}% Off)"
                    )
                else:
                    savings_text += f" (save ${savings:,.2f})"
                html += savings_text
    except (ValueError, AttributeError) as e:
        print(f"Warning: Could not process savings info: {e}")

    html += "\n"

    main_listing = product.offers.listings[0]
    if (
        hasattr(main_listing, "deliveryInfo")
        and hasattr(main_listing.deliveryInfo, "isPrimeEligible")
        and main_listing.deliveryInfo.isPrimeEligible
    ):
        html += "✅ Prime\n"

    if hasattr(main_listing, "promotions") and main_listing.promotions:
        print("\nPromotion details:", dir(main_listing.promotions[0]))
        has_promotions = False

        for promo in main_listing.promotions:
            # Debug promotion information
            print(f"\nPromotion attributes: {dir(promo)}")
            print(f"Promotion type: {getattr(promo, 'type', 'N/A')}")
            print(f"Promotion display style: {getattr(promo, 'displayStyle', 'N/A')}")

            promo_text = ""

            promo_type = getattr(promo, "type", "").lower()
            display_style = getattr(promo, "displayStyle", "").lower()
            discount_percent = getattr(promo, "discount_percent", None)

            if "coupon" in promo_type:
                if "checkbox" in display_style:
                    promo_text = "✅ Checkbox Coupon"
                else:
                    promo_text = "✂️ Clip Coupon"
            elif "deal" in promo_type:
                promo_text = "🏷️ Special Deal"
            elif "lightning" in promo_type:
                promo_text = "⚡ Lightning Deal"
            elif "prime" in promo_type:
                promo_text = "🎯 Prime Deal"
            else:
                promo_text = f"🏷️ {getattr(promo, 'type', 'Promotion')}"

            if hasattr(promo, "amount"):
                try:
                    amount = int(float(promo.amount) * 100) / 100.0
                    if promo_text:
                        promo_text += f" - Save ${amount:,.2f}"
                    else:
                        promo_text = f"💰 Save ${amount:,.2f}"
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not process promotion amount: {e}")

            if discount_percent is not None:
                try:
                    if promo_text:
                        promo_text += f" ({discount_percent}% Off)"
                    else:
                        promo_text = f"💰 {discount_percent}% Off"
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not process discount percentage: {e}")
            elif hasattr(promo, "percentageOff"):
                try:
                    percentage = float(promo.percentageOff)
                    if promo_text:
                        promo_text += f" ({percentage:.0f}% Off)"
                    else:
                        promo_text = f"💰 {percentage:.0f}% Off"
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Could not process percentage off: {e}")

            if promo_text:
                html += f"\n{promo_text}"
                has_promotions = True

        if has_promotions:
            html += "\n"

    if hasattr(main_listing, "savingBasis") and main_listing.savingBasis:
        if hasattr(main_listing.savingBasis, "amount"):
            try:
                list_price = int(float(main_listing.savingBasis.amount) * 100) / 100.0
                html += f"🔥 List Price: ${list_price:,.2f}\n"
            except (ValueError, AttributeError) as e:
                print(f"Warning: Could not process list price: {e}")

    html += f"\n👉🏻 <a href='{product_url}'>Open on Amazon</a>"

    return html
