

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import logging
import requests

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    

def load_data(data_path):
    df = pd.read_excel(data_path)
    return df

def notify_done(message: str):
    topic = 'qwerty'
    title = 'Analysis Code execution '
    # send a message through ntfy.sh
    requests.post(
    'https://ntfy.sh/' + topic,
    data=message.encode('utf-8'),
    headers={'Title': title} )

def plot_monthly_sales(df, dimension, output_filename, title_size, config):

    """
This script analyzes and visualizes monthly sales data from the Sample Superstore dataset.
It provides functionality to plot monthly sales by segment or region and calculate mean sales 
and mean profit for the specified dimension. The results are saved in a text file.

Usage:
    python script_name.py [--dimension {segment, region}] [--output_filename OUTPUT_FILENAME]
                          [--title_size TITLE_SIZE] [--job_config_file JOB_CONFIG_FILE]
                          [--user_config_file USER_CONFIG_FILE] [--log_file LOG_FILE]
                          [--result_output_filename RESULT_OUTPUT_FILENAME]

Args:
    --dimension (str): The dimension to analyze, either 'segment' or 'region'.
    --output_filename (str): The filename to save the plot as a PNG file.
    --title_size (int): The font size for the plot title.
    --job_config_file (str): The job-specific configuration file in YAML format.
    --user_config_file (str): The user-specific configuration file in YAML format.
    --log_file (str): The log file name to record information and errors.
    --result_output_filename (str): The filename to save mean sales and mean profit results.

Examples:
    python script_name.py --dimension segment --output_filename monthly_sales_by_segment.png
                         --title_size 18 --log_file my_log.log
"""
    try:
        # Convert the OrderDate column to datetime format
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])

        # Extract month from the OrderDate column
        df['Month'] = df['Order_Date'].dt.month_name()

        # Group by Month, dimension, and sum the sales
        grouped_data = df.groupby(['Month', dimension])['Sales'].sum().reset_index()

        # Get unique values for the specified dimension
        unique_values = grouped_data[dimension].unique()

        # Plot monthly sales for each value of the dimension on the same graph
        plt.figure(figsize=(config['figure_size']['width'], config['figure_size']['height']))
        sns.set(style="whitegrid")

        for value in unique_values:
            value_data = grouped_data[grouped_data[dimension] == value]
            sns.lineplot(data=value_data, x='Month', y='Sales', label=str(value), marker='o', color=config['plot_color'])

        # Set plot labels and title
        plt.title(config['plot_title'].format(dimension=dimension), fontsize=title_size)
        plt.xlabel(config['plot_x_title'])
        plt.ylabel(config['plot_y_title'])
        plt.legend(title=dimension, loc='upper left')

        # Save the plot as a PNG file
        save_path = config.get('default_save_path', './')
        plt.savefig(save_path + output_filename)

        # Log success
        logging.info(f"Successfully generated plot for {dimension}. Saved as {save_path + output_filename}")

        # Show the plot
        plt.show()

    except ValueError as ve:
        # Log error
        logging.error(f"Error: {ve}")
        logging.error("Please check the data for negative monthly sales.")

def compute_analysis(df, dimension, output_filename, config):

    ''' Calculate the mean of Sales and Profit for the dimensions passsed in parameter'''
    try:
        # Group by dimension and calculate mean sales and mean profit
        mean_data = df.groupby([dimension]).agg({'Sales': 'mean', 'Profit': 'mean'}).reset_index()

        # Save the results to a text file
        save_path = config.get('default_save_path', './')
        result_file_path = save_path + output_filename
        mean_data.to_excel(result_file_path)

        # Log success
        logging.info(f"Mean sales and mean profit calculated for {dimension}. Results saved as {result_file_path}")

    except Exception as e:
        # Log error
        logging.error(f"Error: {e}")
        logging.error("An error occurred while calculating mean sales and mean profit.")

def Analysis():
    parser = argparse.ArgumentParser(description='Plot monthly sales by segment or region.')
    parser.add_argument('--dimension', choices=['Segment', 'Region','State'], required=True,
                        help='Specify whether to plot by segment or region.')
    parser.add_argument('--output_filename', required=True,
                        help='Specify the filename to save the plot as a PNG file.')
    parser.add_argument('--title_size', type=int, default=16,
                        help='Specify the font size for the plot title.')
    parser.add_argument('--job_config_file', default='job_config.yaml',
                        help='Specify the job-specific configuration file.')
    parser.add_argument('--user_config_file', default='user_config.yaml',
                        help='Specify the user-specific configuration file.')
    parser.add_argument('--log_file', default='plotting.log',
                        help='Specify the log file name.')
    parser.add_argument('--result_output_filename', default='mean_sales_profit_results.txt',
                        help='Specify the filename to save mean sales and mean profit results.')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_file)

    # Load job-specific and user configurations
    job_config = load_config(args.job_config_file)
    user_config = load_config(args.user_config_file)

    # Merge user_config into job_config, giving priority to user_config
    config = {**job_config, **user_config}


    data_path = 'sstore.xlsx'
    df=load_data(data_path)


    # Read the Sample Superstore data
#    df = pd.read_excel('sstore.xlsx')

    # Call the function to plot monthly sales based on the specified dimension
    plot_monthly_sales(df, args.dimension, args.output_filename, args.title_size, config)

    # Call the function to calculate mean sales and mean profit for the specified dimension
    compute_analysis(df, args.dimension, args.result_output_filename, config)


    message = 'Mean Calculation and Graph generation completed !!!'
    notify_done(message)


if __name__ == "__main__":
    Analysis()