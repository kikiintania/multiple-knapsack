import streamlit as st
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to read data from CSV file using pandas
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Function to get unique cities from the dataset
def get_cities(df):
    return df['city'].unique().tolist()

# Function to filter data for a specific city
def filter_data_by_city(df, city):
    return df[df['city'] == city]

# Knapsack solver function
def knapsack_solver(items, num_bins, max_weight, max_price):
    model = gp.Model("multiple_knapsack_with_constraints")

    num_items = len(items)

    # Decision variables
    x = model.addVars(num_items, num_bins, vtype=GRB.BINARY, name="x")

    # Objective function (maximize total rating)
    model.setObjective(sum(items.iloc[i]['rating'] * x[i, k] for i in range(num_items) for k in range(num_bins)), GRB.MAXIMIZE)

    # Constraint: each item can only be placed in one knapsack
    model.addConstrs((gp.quicksum(x[i, k] for k in range(num_bins)) 
                      <= 1 for i in range(num_items)), name="item")

    # Constraint: total weight in each knapsack should not exceed the capacity
    model.addConstrs((gp.quicksum(items.iloc[i]['weight'] * x[i, k] for i in range(num_items)) 
                      <= max_weight for k in range(num_bins)), name="weight")

    # Constraint: total price in each knapsack should not exceed the price capacity
    model.addConstrs((gp.quicksum(items.iloc[i]['price'] * x[i, k] for i in range(num_items)) 
                      <= max_price for k in range(num_bins)), name="price")

    # Solve the model
    model.optimize()

    # Get results
    result = []
    if model.status == GRB.OPTIMAL:
        for k in range(num_bins):
            bin_items = [i for i in range(num_items) if x[i, k].X > 0.5]
            if bin_items:
                bin_result = {"bin": k + 1, "items": [], "total_weight": 0, "total_price": 0, "total_rating": 0}
                for i in bin_items:
                    bin_result["items"].append({
                        "item": items.iloc[i]['item'],
                        "weight": float(f"{items.iloc[i]['weight']:.2f}".rstrip('0').rstrip('.')),
                        "price": float(f"{items.iloc[i]['price']:.2f}".rstrip('0').rstrip('.')),
                        "rating": items.iloc[i]['rating']
                    })
                    bin_result["total_weight"] += items.iloc[i]['weight']
                    bin_result["total_price"] += items.iloc[i]['price']
                    bin_result["total_rating"] += items.iloc[i]['rating']
                result.append(bin_result)
    return result

# Evaluation function
def evaluate_solution(result, num_bins, max_weight, max_price, total_items):
    total_rating = sum(bin_result['total_rating'] for bin_result in result)
    total_weight = sum(bin_result['total_weight'] for bin_result in result)
    total_price = sum(bin_result['total_price'] for bin_result in result)
    items_used = sum(len(bin_result['items']) for bin_result in result)
    bins_used = len(result)
    
    weight_utilization = total_weight / (num_bins * max_weight) * 100
    price_utilization = total_price / (num_bins * max_price) * 100
    item_utilization = items_used / total_items * 100
    bin_utilization = bins_used / num_bins * 100
    
    evaluation = {
        "Total Rating": total_rating,
        "Total Weight": total_weight,
        "Total Price": total_price,
        "Items Used": items_used,
        "Bins Used": bins_used,
        "Weight Utilization (%)": weight_utilization,
        "Price Utilization (%)": price_utilization,
        "Item Utilization (%)": item_utilization,
        "Bin Utilization (%)": bin_utilization
    }
    
    return evaluation

# Streamlit app
def main():
    st.title("Knapsack Problem Solver")

    # Load data
    df = load_data('dummy_dataset.csv')
    
    # Get unique cities
    cities = get_cities(df)
    
    # Dropdown for city selection
    selected_city = st.selectbox("Select a city", cities)
    
    # Filter data for the selected city
    city_data = filter_data_by_city(df, selected_city)
    
    # Display data table
    st.write(f"Data for {selected_city}")
    st.dataframe(city_data)
    
    # Get user inputs
    num_bins = st.number_input("Enter the number of knapsacks:", min_value=1, value=3)
    max_weight = st.number_input("Enter the maximum weight capacity for each knapsack:", min_value=0.0, value=50.0, format="%.2f")
    max_price = st.number_input("Enter the maximum price capacity for each knapsack:", min_value=0.0, value=100.0, format="%.2f")
    
    # Solve the knapsack problem
    if st.button("Solve"):
        result = knapsack_solver(city_data, num_bins, max_weight, max_price)
        
        # Display results
        if result:
            st.write(f"\nResults for {selected_city}:")
            for bin_result in result:
                st.write(f"\nBin {bin_result['bin']}")
                st.write(f"Total weight: {bin_result['total_weight']:.2f}")
                st.write(f"Total price: {bin_result['total_price']:.2f}")
                st.write(f"Total rating: {bin_result['total_rating']:.2f}")
                for item in bin_result["items"]:
                    st.write(f"Item: {item['item']}, Weight: {item['weight']:.2f}, Price: {item['price']:.2f}, Rating: {item['rating']:.2f}")
            
            # Evaluate the solution
            evaluation = evaluate_solution(result, num_bins, max_weight, max_price, len(city_data))
            
            st.subheader("Solution Evaluation:")
            st.write("\n")
            for metric, value in evaluation.items():
                st.write(f"{metric}: {value:.2f}")
                
            # Prepare results for download
            result_df = pd.DataFrame([
                {"Bin": bin_result['bin'], "Item": item['item'], "Weight": item['weight'], "Price": item['price'], "Rating": item['rating']}
                for bin_result in result
                for item in bin_result['items']
            ])
            csv = result_df.to_csv(index=False)
            st.download_button(label="Download Results as CSV", data=csv, file_name='knapsack_results.csv', mime='text/csv')
        else:
            st.write("The problem does not have an optimal solution.")

if __name__ == "__main__":
    main()
