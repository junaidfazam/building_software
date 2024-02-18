import pandas as pd
import pytest
import glob
import openpyxl
from Analysis import compute_analysis


@pytest.fixture
def sample_data():
    # Assuming 'sample_data.xlsx' contains the test data
    return pd.read_excel('sample_data.xlsx')

@pytest.fixture
def expected_results():
    # Assuming 'expected_results.xlsx' contains the expected results
    return pd.read_excel('expected_results.xlsx')

def test_compute_analysis(sample_data, expected_results):
    dimension = 'Segment'
    output_filename = 'test_results.xlsx'
    #config = {'default_save_path': str(tmp_path)}
    config = {'default_save_path': './'}

    # Call the function to calculate mean sales and mean profit for the specified dimension
    compute_analysis(sample_data, dimension, output_filename, config)

    # Load the actual results from the generated text file
    actual_results = pd.read_excel('test_results.xlsx',engine="openpyxl", index_col=0)

    # Ensure the actual results match the expected results
    pd.testing.assert_frame_equal(actual_results, expected_results)

   

    