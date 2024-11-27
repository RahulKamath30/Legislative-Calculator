import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
from country_manager import CountryDataManager, LegislativeCalculatorEnhanced

def main():
    st.set_page_config(page_title="Legislative Success Calculator", layout="wide")
    
    # Initialize the data manager with the JSON file path
    try:
        data_manager = CountryDataManager('data/factbook.json')
        calculator = LegislativeCalculatorEnhanced(data_manager)
        
        st.title("Legislative Success Probability Calculator")
        st.markdown("""
        This calculator predicts the likelihood of a bill's passage based on various political and social factors.
        Choose your country and adjust the sliders to analyze your bill.
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Bill Information")
            
            # Country selection from available countries in factbook
            available_countries = data_manager.get_all_country_names()
            country = st.selectbox("Select Country", available_countries)
            
            # Get country system info
            country_system = data_manager.get_country_system(country)
            if country_system:
                st.info(f"""
                System Type: {country_system['system_type']}
                Legislature Type: {country_system['legislature_type']}
                """)
            
            bill_name = st.text_input("Enter Bill Name", "New Bill")
            
            # Dynamic factor inputs based on country
            factors = {}
            
            # Basic factors for all countries
            factors['governing_party_support'] = st.slider(
                "Governing Party Support", 0.0, 1.0, 0.8,
                help="Level of support from the governing party"
            )
            
            factors['opposition_support'] = st.slider(
                "Opposition Support", 0.0, 1.0, 0.3,
                help="Level of support from opposition parties"
            )
            
            factors['public_opinion'] = st.slider(
                "Public Opinion", 0.0, 1.0, 0.7,
                help="Level of public support"
            )
            
            factors['committee_approval'] = st.slider(
                "Committee Approval", 0.0, 1.0, 0.9,
                help="Level of support from relevant committees"
            )
            
            # Add bicameral-specific factors if applicable
            if country_system and country_system['legislature_type'] == 'bicameral':
                factors['upper_house_support'] = st.slider(
                    "Upper House Support", 0.0, 1.0, 0.8,
                    help="Level of support in upper house"
                )
                factors['lower_house_support'] = st.slider(
                    "Lower House Support", 0.0, 1.0, 0.8,
                    help="Level of support in lower house"
                )
            
            # Common factors continued
            factors['fiscal_impact'] = st.slider(
                "Fiscal Impact", 0.0, 1.0, 0.6,
                help="Positive fiscal impact"
            )
            
            factors['urgency_factor'] = st.slider(
                "Urgency Factor", 0.0, 1.0, 0.8,
                help="How urgent is the bill"
            )
            
            factors['previous_similar_bills'] = st.slider(
                "Previous Similar Bills Success", 0.0, 1.0, 0.7,
                help="Success rate of similar bills"
            )
            
            factors['media_coverage'] = st.slider(
                "Media Coverage", 0.0, 1.0, 0.6,
                help="Favorability of media coverage"
            )
        
        # Calculate probability using the enhanced calculator
        probability, breakdown = calculator.calculate_probability(country, factors)
        interpretation = calculator.get_interpretation(probability)
        
        with col2:
            st.subheader("Analysis Results")
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probability * 100,
                title={'text': "Passage Probability"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 20], 'color': "red"},
                        {'range': [20, 40], 'color': "orange"},
                        {'range': [40, 60], 'color': "yellow"},
                        {'range': [60, 80], 'color': "lightgreen"},
                        {'range': [80, 100], 'color': "green"}
                    ]
                }
            ))
            
            st.plotly_chart(fig)
            
            st.markdown(f"### Interpretation")
            st.markdown(f"**{interpretation}**")
            
            if country_system:
                st.markdown("### System Information")
                st.json(country_system)
            
            st.markdown("### Factor Breakdown")
            breakdown_df = pd.DataFrame([
                {
                    'Factor': k.replace('_', ' ').title(),
                    'Score': f"{v['raw_score']:.1%}",
                    'Weight': f"{v['weight']:.1%}",
                    'Impact': f"{v['weighted_score']:.1%}"
                }
                for k, v in breakdown.items()
            ])
            st.dataframe(breakdown_df, hide_index=True)
            
    except Exception as e:
        st.error(f"Error loading country data: {str(e)}")
        st.info("Please check if the factbook.json file is properly placed in the data folder.")

if __name__ == "__main__":
    main()
