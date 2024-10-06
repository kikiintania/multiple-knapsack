import gurobipy as gp
from gurobipy import GRB
import pandas as pd

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
                        "weight": items.iloc[i]['weight'],
                        "price": items.iloc[i]['price'],
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

# Main execution
if __name__ == "__main__":
    # Load data
    df = load_data('dummy_dataset.csv')
    
    # Get unique cities
    cities = get_cities(df)
    
    # Display cities and let user choose
    print("Available cities:")
    for i, city in enumerate(cities):
        print(f"{i + 1}. {city}")
    
    city_choice = int(input("Enter the number of the city you want to analyze: ")) - 1
    selected_city = cities[city_choice]
    
    # Filter data for the selected city
    city_data = filter_data_by_city(df, selected_city)
    
    # Get user inputs
    num_bins = int(input("Enter the number of knapsacks: "))
    max_weight = float(input("Enter the maximum weight capacity for each knapsack: "))
    max_price = float(input("Enter the maximum price capacity for each knapsack: "))
    
    # Solve the knapsack problem
    result = knapsack_solver(city_data, num_bins, max_weight, max_price)
    
    # Display results
    if result:
        print(f"\nResults for {selected_city}:")
        for bin_result in result:
            print(f"\nBin {bin_result['bin']}")
            print(f"Total weight: {bin_result['total_weight']:.2f}")
            print(f"Total price: {bin_result['total_price']:.2f}")
            print(f"Total rating: {bin_result['total_rating']:.2f}")
            for item in bin_result["items"]:
                print(f"Item: {item['item']}, Weight: {item['weight']:.2f}, Price: {item['price']:.2f}, Rating: {item['rating']:.2f}")
        
        # Evaluate the solution
        evaluation = evaluate_solution(result, num_bins, max_weight, max_price, len(city_data))
        
        print("\nSolution Evaluation:")
        for metric, value in evaluation.items():
            print(f"{metric}: {value:.2f}")
    else:
        print("The problem does not have an optimal solution.")
