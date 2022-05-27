from recommender.cataloguebp.models import Brand, Category, StatusType, Product,Base
from recommender.arlbp.arl_service import to_frozenset,get_rules_table
import pandas as pd
from sqlalchemy import select
from flask import session


def recommender_ids():
    rules_dict = get_rules_table()
    rules = pd.DataFrame(rules_dict)
    rules[["antecedents","consequents"]] = rules[["antecedents","consequents"]].applymap(to_frozenset)
    product_ids = []
    for set in rules["antecedents"].unique():
        for id in set:
            if id not in product_ids:
                product_ids.append(id)
    return product_ids

def fetch_products(request, category_slug, brand_slug):

       page = int(request.args.get('page', 1))
       product_ids = recommender_ids()

        #Filter the products
       if category_slug == 'all-categories' and  brand_slug == 'all-brands':
            page_object = Product.query.filter_by(product_status = StatusType.Active).filter(Product.id.in_(product_ids)).paginate(page, 9,  False)

       if category_slug != 'all-categories' and  brand_slug != 'all-brands':
            page_object =  (Product.query.filter_by(product_status =  StatusType.Active)
                              .filter(Product.categories.any(Category.slug ==  category_slug))
                              .filter(Product.brands.any(Brand.slug == brand_slug)).filter(Product.id.in_(product_ids)).paginate(page, 9,  False)
                             )
       if category_slug != 'all-categories' and  brand_slug == 'all-brands':
            page_object =  (Product.query.filter_by(product_status =  StatusType.Active)
                               .filter(Product.categories.any(Category.slug ==  category_slug)).filter(Product.id.in_(product_ids)).paginate(page, 9,  False)
                            )
       if category_slug == 'all-categories' and  brand_slug != 'all-brands':
            page_object =  (Product.query.filter_by(product_status =  StatusType.Active)
                              .filter(Product.brands.any(Brand.slug == brand_slug)).filter(Product.id.in_(product_ids)).paginate(page, 9,  False)
                             )
              
       return page_object

def product_details(request,product_slug):

    product_details = Product.query.filter_by(slug = product_slug).first()

    return product_details


   # The page_object has the following properties and methods:
   # items, pages, prev_num, next_num, iter_pages(), page, has_next, has_prev 
