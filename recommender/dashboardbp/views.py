from flask import (Blueprint, request, render_template, url_for, redirect)
from datetime import datetime
from recommender.dashboardbp import dashboard_service 

# RFM ile segmentasyon 
# Custsomer lifetime value prediction
# Churn prediction


dashboard_blueprint = Blueprint("dashboard", __name__ ,template_folder = "templates/dashboardbp")
@dashboard_blueprint.route('/dashboard', methods=['GET','POST'])
def dashboard():

    if request.method == "POST":

        return render_template(
           'dashboard_home.html',
           title='Dashboard',
           year=datetime.now().year,
         )
    else:
        kpis = dashboard_service.home_kpis()
        customer_ids,num_orders, product_names, num_sales,lineplot_dict,pie_dict = dashboard_service.home_charts()
        print(pie_dict)
        return render_template(
           'dashboard_home.html',
           title='Dashboard',
           year=datetime.now().year,
           kpis = kpis,
           customer_ids = customer_ids,
           num_orders = num_orders,
           product_names = product_names,
           num_sales = num_sales,
           lineplot_dict = lineplot_dict,
           pie_dict = pie_dict

         )

@dashboard_blueprint.route('/dashboard/rfm', methods=['GET','POST'])
def dashboard_rfm():
    l_segments = dashboard_service.fetch_segments()
    l_countries = dashboard_service.fetch_countries()
    avg_rfm,avg_rfm_score = dashboard_service.rfm_kpis()
    segment_names,customer_count,scatter_freq_dict,scatter_recency_dict,datasets_freq,datasets_recency = dashboard_service.rfm_charts()
    customer_ratios = ["%" + str(round(i/sum(customer_count) * 100)) for i in customer_count]

    
    if request.method == "POST":
        customer_segment = dashboard_service.fetch_customer_segment(request)

        return render_template(
           'dashboard_rfm.html',
           title='Dashboard',
           year=datetime.now().year,
           l_segments = l_segments,
           l_countries = l_countries,
           customer_segment = customer_segment,
           avg_rfm = avg_rfm,
           avg_rfm_score = avg_rfm_score,
           segment_names = segment_names,
           customer_count = customer_count,
           customer_ratios = customer_ratios,
           scatter_freq_dict = scatter_freq_dict,
           scatter_recency_dict = scatter_recency_dict,
           datasets_freq = datasets_freq,
           datasets_recency = datasets_recency

         )

    else:
        customer_segment = dashboard_service.fetch_rfm_onload()
        return render_template(
           'dashboard_rfm.html',
           title='Dashboard',
           year=datetime.now().year,
           l_segments = l_segments,
           l_countries = l_countries,
           customer_segment = customer_segment,
           avg_rfm = avg_rfm,
           avg_rfm_score = avg_rfm_score,
           segment_names = segment_names,
           customer_count = customer_count,
           customer_ratios = customer_ratios,
           scatter_freq_dict = scatter_freq_dict,
           scatter_recency_dict = scatter_recency_dict,
           datasets_freq = datasets_freq,
           datasets_recency = datasets_recency
         )


@dashboard_blueprint.route('/dashboard/customer-lifetime', methods=['GET','POST'])
def dashboard_cltv():
    kpis = dashboard_service.cltv_kpis()
    cltv_table = dashboard_service.fetch_cltv_onload()
    top_customers_id,top_customers_value,value_name,cltv_dict,line_value,scatter_plot_dict_freq,scatter_plot_dict_order = dashboard_service.cltv_bar_chart(request)


    if request.method == "POST":
        return render_template(
           'dashboard_clv.html',
           title='Customer Lifetime Value',
           year=datetime.now().year,
           kpis = kpis,
           cltv_table = cltv_table,
           top_customers_id = top_customers_id,
           top_customers_value = top_customers_value,
           value_name = value_name,
           cltv_dict = cltv_dict,
           line_value = line_value,
           scatter_plot_dict_freq = scatter_plot_dict_freq,
           scatter_plot_dict_order = scatter_plot_dict_order

         )

    else:
        return render_template(
           'dashboard_clv.html',
           title='Customer Lifetime Value',
           year=datetime.now().year,
           kpis = kpis,
           cltv_table = cltv_table,
           top_customers_id = top_customers_id,
           top_customers_value = top_customers_value,
           value_name = value_name,
           cltv_dict = cltv_dict,
           line_value = line_value,
           scatter_plot_dict_freq = scatter_plot_dict_freq,
           scatter_plot_dict_order = scatter_plot_dict_order
         )

@dashboard_blueprint.route('/dashboard/customer-lifetime-prediction', methods=['GET','POST'])
def dashboard_cltv_prediction():
    kpis,cltvp_table,months = dashboard_service.cltv_prediction_kpis_table(request)
    top_customers_ids,top_customers_values,bar_chart_value,dist_plot_dict,dist_plot_value,scatter_plot_dict_transaction,scatter_plot_dict_profit = dashboard_service.cltv_prediction_charts(request,cltvp_table)
    
    if request.method == "POST":
        return render_template(
           'dashboard_clvp.html',
           title='Customer Lifetime Value Prediction',
           year=datetime.now().year,
           kpis = kpis,
           cltvp_table = cltvp_table,
           top_customers_ids = top_customers_ids,
           top_customers_values = top_customers_values,
           bar_chart_value = bar_chart_value,
           dist_plot_dict = dist_plot_dict,
           dist_plot_value = dist_plot_value,
           months = months,
           scatter_plot_dict_transaction = scatter_plot_dict_transaction,
           scatter_plot_dict_profit = scatter_plot_dict_profit

         )

    else:
        return render_template(
           'dashboard_clvp.html',
           title='Customer Lifetime Value Prediction',
           year=datetime.now().year,
           kpis = kpis,
           cltvp_table = cltvp_table,
           top_customers_ids = top_customers_ids,
           top_customers_values = top_customers_values,
           bar_chart_value = bar_chart_value,
           dist_plot_dict = dist_plot_dict,
           dist_plot_value = dist_plot_value,
           months = months,
           scatter_plot_dict_transaction = scatter_plot_dict_transaction,
           scatter_plot_dict_profit = scatter_plot_dict_profit
         )





