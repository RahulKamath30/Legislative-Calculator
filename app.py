import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import base64
from io import BytesIO
import plotly.express as px

class LegislativeSystem:
    def __init__(self, name, is_bicameral, governing_party_weight=0.30):
        self.name = name
        self.is_bicameral = is_bicameral
        self.weights = {
            'governing_party_support': governing_party_weight,
            'opposition_support': 0.15,
            'public_opinion': 0.10,
            'committee_approval': 0.20,
            'fiscal_impact': 0.10,
            'urgency_factor': 0.05,
            'previous_similar_bills': 0.05,
            'media_coverage': 0.05
        }
        if is_bicameral:
            # Adjust weights for bicameral system
            self.weights['upper_house_support'] = 0.15
            self.weights['lower_house_support'] = 0.15
            # Reduce other weights proportionally
            for key in self.weights:
                if key not in ['upper_house_support', 'lower_house_support']:
                    self.weights[key] *= 0.7

class LegislativeCalculator:
    def __init__(self):
        self.systems = {
            'Singapore': LegislativeSystem('Singapore', False),
            'United States': LegislativeSystem('United States', True),
            'United Kingdom': LegislativeSystem('United Kingdom', True),
            'New Zealand': LegislativeSystem('New Zealand', False),
            'Australia': LegislativeSystem('Australia', True)
        }
        self.saved_bills = {}

    def calculate_probability(self, bill_factors, country):
        system = self.systems[country]
        total_score = 0
        factor_breakdown = {}
        
        for factor, weight in system.weights.items():
            if factor in bill_factors:
                score = bill_factors[factor] * weight
                total_score += score
                factor_breakdown[factor] = {
                    'raw_score': bill_factors[factor],
                    'weight': weight,
                    'weighted_score': score
                }
        
        final_probability = max(0, min(1, total_score))
        return final_probability, factor_breakdown

    def get_interpretation(self, probability):
        if probability >= 0.8:
            return "Very High Probability of Passage"
        elif probability >= 0.6:
            return "High Probability of Passage"
        elif probability >= 0.4:
            return "Moderate Probability of Passage"
        elif probability >= 0.2:
            return "Low Probability of Passage"
        else:
            return "Very Low Probability of Passage"

    def generate_pdf_report(self, bill_name, country, probability, breakdown, interpretation):
        report = f"""
        Legislative Analysis Report
        -------------------------
        Bill Name: {bill_name}
        Country: {country}
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Overall Probability: {probability:.1%}
        Interpretation: {interpretation}
        
        Factor Breakdown:
        """
        for factor, details in breakdown.items():
            report += f"\n{factor.replace('_', ' ').title()}:"
            report += f"\n  Score: {details['raw_score']:.1%}"
            report += f"\n  Weight: {details['weight']:.1%}"
            report += f"\n  Impact: {details['weighted_score']:.1%}"
        
        return report

def main():
    st.set_page_config(page_title="Legislative Success Calculator", layout="wide")
    
    calculator = LegislativeCalculator()
    
    st.title("Legislative Success Probability Calculator")
    st.markdown("""
    This calculator helps predict the likelihood of a bill's passage based on various political and social factors.
    Choose your country and adjust the sliders to analyze your bill.
    """)
    
    # Session State for saved bills
    if 'saved_bills' not in st.session_state:
        st.session_state.saved_bills = {}
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Bill Information")
        
        # Country selection
        country = st.selectbox("Select Country", list(calculator.systems.keys()))
        system = calculator.systems[country]
        
        bill_name = st.text_input("Enter Bill Name", "New Bill")
        
        # Dynamic factor inputs based on country
        factors = {}
        
        # Common factors for all countries
        common_factors = [
            ('governing_party_support', "Governing Party Support"),
            ('opposition_support', "Opposition Support"),
            ('public_opinion', "Public Opinion"),
            ('committee_approval', "Committee Approval"),
            ('fiscal_impact', "Fiscal Impact"),
            ('urgency_factor', "Urgency Factor"),
            ('previous_similar_bills', "Previous Similar Bills Success"),
            ('media_coverage', "Media Coverage")
        ]
        
        for key, label in common_factors:
            factors[key] = st.slider(
                label, 0.0, 1.0, 0.8,
                help=f"Set the level of {label.lower()} (0 = lowest, 1 = highest)"
            )
        
        # Additional factors for bicameral systems
        if system.is_bicameral:
            factors['upper_house_support'] = st.slider(
                "Upper House Support", 0.0, 1.0, 0.8,
                help="Level of support in the upper house"
            )
            factors['lower_house_support'] = st.slider(
                "Lower House Support", 0.0, 1.0, 0.8,
                help="Level of support in the lower house"
            )
    
    # Calculate probability
    probability, breakdown = calculator.calculate_probability(factors, country)
    interpretation = calculator.get_interpretation(probability)
    
    with col2:
        st.subheader("Analysis Results")
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = probability * 100,
            title = {'text': "Passage Probability"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
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
        
        # Save bill analysis
        if st.button("Save Current Analysis"):
            st.session_state.saved_bills[f"{bill_name} ({country})"] = {
                'name': bill_name,
                'country': country,
                'probability': probability,
                'factors': factors,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            st.success("Analysis saved!")
        
        # Generate PDF report
        if st.button("Generate PDF Report"):
            report = calculator.generate_pdf_report(
                bill_name, country, probability, breakdown, interpretation
            )
            b64 = base64.b64encode(report.encode()).decode()
            href = f'<a href="data:text/plain;base64,{b64}" download="{bill_name}_analysis.txt">Download Analysis Report</a>'
            st.markdown(href, unsafe_allow_html=True)
    
    # Saved Bills Analysis
    if st.session_state.saved_bills:
        st.subheader("Saved Bills Comparison")
        comparison_data = []
        for saved_bill in st.session_state.saved_bills.values():
            comparison_data.append({
                'Bill Name': saved_bill['name'],
                'Country': saved_bill['country'],
                'Probability': saved_bill['probability'],
                'Timestamp': saved_bill['timestamp']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, hide_index=True)
        
        # Comparison chart
        fig_compare = px.bar(
            comparison_df, 
            x='Bill Name', 
            y='Probability',
            color='Country',
            title='Comparison of Saved Bills',
            labels={'Probability': 'Passage Probability'}
        )
        st.plotly_chart(fig_compare)

if __name__ == "__main__":
    main()
