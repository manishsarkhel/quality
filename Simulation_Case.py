import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def main():
    st.title("Manufacturing Process Simulator")
    st.write("Apply normal distribution concepts to quality control in manufacturing")
    
    # Sidebar controls for manufacturing scenario
    st.sidebar.header("Process Parameters")
    target_dimension = st.sidebar.number_input("Target Dimension (mm)", 10.0, 100.0, 25.0, 0.1)
    process_mean = st.sidebar.number_input("Actual Process Mean (mm)", 10.0, 100.0, 25.003, 0.001)
    process_std = st.sidebar.number_input("Process Standard Deviation (mm)", 0.001, 1.0, 0.018, 0.001)
    lower_spec = st.sidebar.number_input("Lower Specification Limit (mm)", 10.0, 100.0, target_dimension - 0.05, 0.001)
    upper_spec = st.sidebar.number_input("Upper Specification Limit (mm)", 10.0, 100.0, target_dimension + 0.05, 0.001)
    
    # Production parameters
    st.sidebar.header("Production Parameters")
    batch_size = st.sidebar.number_input("Batch Size", 100, 10000, 1000, 100)
    cost_per_unit = st.sidebar.number_input("Manufacturing Cost per Unit ($)", 0.1, 100.0, 5.0, 0.1)
    revenue_per_unit = st.sidebar.number_input("Revenue per Good Unit ($)", 0.1, 200.0, 15.0, 0.1)
    
    # Generate manufactured parts (simulated)
    manufactured_parts = np.random.normal(process_mean, process_std, batch_size)
    
    # Calculate defect rate
    defects = np.sum((manufactured_parts < lower_spec) | (manufactured_parts > upper_spec))
    defect_rate = defects / batch_size * 100
    
    # Financial impact
    total_manufacturing_cost = batch_size * cost_per_unit
    good_parts = batch_size - defects
    total_revenue = good_parts * revenue_per_unit
    profit = total_revenue - total_manufacturing_cost
    
    # Calculate process capability indices
    cp = (upper_spec - lower_spec) / (6 * process_std)
    cpu = (upper_spec - process_mean) / (3 * process_std)
    cpl = (process_mean - lower_spec) / (3 * process_std)
    cpk = min(cpu, cpl)
    
    # Plot the distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Generate points for plotting the normal curve
    x = np.linspace(process_mean - 4*process_std, process_mean + 4*process_std, 1000)
    pdf = stats.norm.pdf(x, process_mean, process_std)
    
    # Plot the PDF
    ax.plot(x, pdf, 'b-', lw=2, label='Process Distribution')
    
    # Fill the areas within specification
    in_spec_x = x[(x >= lower_spec) & (x <= upper_spec)]
    in_spec_pdf = pdf[(x >= lower_spec) & (x <= upper_spec)]
    ax.fill_between(in_spec_x, in_spec_pdf, color='green', alpha=0.3, label='Within Spec')
    
    # Fill the areas outside specification
    lower_out_x = x[x < lower_spec]
    lower_out_pdf = pdf[x < lower_spec]
    upper_out_x = x[x > upper_spec]
    upper_out_pdf = pdf[x > upper_spec]
    
    ax.fill_between(lower_out_x, lower_out_pdf, color='red', alpha=0.3, label='Below Spec')
    ax.fill_between(upper_out_x, upper_out_pdf, color='red', alpha=0.3, label='Above Spec')
    
    # Add specification lines
    ax.axvline(lower_spec, color='red', linestyle='--', label='Lower Spec Limit')
    ax.axvline(upper_spec, color='red', linestyle='--', label='Upper Spec Limit')
    ax.axvline(target_dimension, color='black', linestyle='-', label='Target')
    ax.axvline(process_mean, color='blue', linestyle='--', label='Process Mean')
    
    # Histogram of actual produced parts
    ax.hist(manufactured_parts, bins=30, density=True, alpha=0.2, color='gray', label='Simulated Parts')
    
    # Set plot labels and title
    ax.set_xlabel('Dimension (mm)')
    ax.set_ylabel('Probability Density')
    ax.set_title(f'Manufacturing Process Distribution')
    ax.legend()
    
    # Display the plot
    st.pyplot(fig)
    
    # Display process statistics
    st.header("Process Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Process Metrics")
        st.write(f"Process Mean: {process_mean:.6f} mm")
        st.write(f"Process Std Dev: {process_std:.6f} mm")
        st.write(f"Defect Rate: {defect_rate:.2f}%")
        st.write(f"Process Capability (Cp): {cp:.3f}")
        st.write(f"Process Capability Index (Cpk): {cpk:.3f}")
        
        if cpk < 1.0:
            st.error("Process is not capable (Cpk < 1.0)")
        elif cpk < 1.33:
            st.warning("Process is marginally capable (1.0 ≤ Cpk < 1.33)")
        else:
            st.success("Process is capable (Cpk ≥ 1.33)")
            
    with col2:
        st.subheader("Financial Impact")
        st.write(f"Good Parts: {good_parts} units")
        st.write(f"Defective Parts: {defects} units")
        st.write(f"Total Manufacturing Cost: ${total_manufacturing_cost:.2f}")
        st.write(f"Total Revenue: ${total_revenue:.2f}")
        st.write(f"Profit: ${profit:.2f}")
        
        if profit < 0:
            st.error(f"The process is operating at a loss")
        else:
            st.success(f"The process is profitable")
    
    # Process improvement scenarios
    st.header("Process Improvement Scenarios")
    st.write("Explore how improving the process affects defect rates and profits:")
    
    improved_std = st.slider("Improved Process Std Dev (mm)", 0.001, process_std*2, process_std*0.8, 0.001)
    centered_mean = st.checkbox("Center Process Mean to Target", False)
    
    improved_mean = target_dimension if centered_mean else process_mean
    
    # Calculate new defect rates and financial outcomes
    z_lower_improved = (lower_spec - improved_mean) / improved_std
    z_upper_improved = (upper_spec - improved_mean) / improved_std
    
    defect_rate_improved = (1 - (stats.norm.cdf(z_upper_improved) - stats.norm.cdf(z_lower_improved))) * 100
    good_parts_improved = batch_size * (1 - defect_rate_improved/100)
    total_revenue_improved = good_parts_improved * revenue_per_unit
    
    # Add cost of improvement
    improvement_cost = st.number_input("Investment for Process Improvement ($)", 0, 100000, 5000, 100)
    profit_improved = total_revenue_improved - total_manufacturing_cost - improvement_cost
    roi = (profit_improved - profit) / improvement_cost * 100 if improvement_cost > 0 else float('inf')
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Process")
        st.write(f"Defect Rate: {defect_rate:.2f}%")
        st.write(f"Profit: ${profit:.2f}")
        st.write(f"Cpk: {cpk:.3f}")
        
    with col2:
        st.subheader("Improved Process")
        st.write(f"Defect Rate: {defect_rate_improved:.2f}%")
        st.write(f"Profit: ${profit_improved:.2f}")
        st.write(f"ROI on Improvement: {roi:.1f}%")
        st.write(f"Cpk: {min((upper_spec - improved_mean) / (3 * improved_std), (improved_mean - lower_spec) / (3 * improved_std)):.3f}")
    
    # In-class discussion prompts
    st.header("Discussion Questions")
    st.write("1. What is the relationship between process standard deviation and defect rate?")
    st.write("2. How does centering the process mean on the target value affect process capability?")
    st.write("3. At what point does investing in process improvement become financially viable?")
    st.write("4. How would you determine the optimal sampling plan for this manufacturing process?")
    st.write("5. What would be the impact of changing the specification limits on defect rates and profitability?")

if __name__ == "__main__":
    main()