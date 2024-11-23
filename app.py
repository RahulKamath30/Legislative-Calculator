import streamlit as st
import pandas as pd
import plotly.graph_objects as go

class LegislativeCalculator:
    def __init__(self):
        self.weights = {
            'governing_party_support': 0.25,
            'opposition_support': 0.15,
            'public_opinion': 0.15,
            'committee_approval': 0.20,
            'fiscal_impact': 0.10,
            'urgency_factor': 0.05,
            'previous_similar_bills': 0.05,
            'media_coverage': 0.05
        }
    
    def calculate_probability(self, bill_factors):
        total_score = 0
        factor_breakdown = {}
        
        for factor, weight in self.weights.items():
            score = bill_factors[factor] * weight
            total_score += score
            factor_breakdown[factor] = {
                'raw_score': bill_factors[factor],
                'weight': weight,
                'weighted_score': score
            }
            
        if bill_factors['governing_party_support'] < 0.3:
            total_score *= 0.5
            
        if bill_factors['committee_approval'] < 0.2:
            total_score *= 0.7
            
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

def main():
    st.set_page_config(page_title="Legislative Success Calculator", layout="wide")
    
    st.title("Legislative Success Probability Calculator")
    st.markdown("""
    This calculator helps predict the likelihood of a bill's passage based on various political and social factors.
    Adjust the sliders below to analyze your bill.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Bill Information")
        bill_name = st.text_input("Enter Bill Name", "New Bill")
        
        factors = {}
        factors['governing_party_support'] = st.slider(
            "Governing Party Support", 0.0, 1.0, 0.8,
            help="Level of support from the governing party (0 = no support, 1 = full support)"
        )
        factors['opposition_support'] = st.slider(
            "Opposition Support", 0.0, 1.0, 0.3,
            help="Level of support from opposition parties"
        )
        factors['public_opinion'] = st.slider(
            "Public Opinion", 0.0, 1.0, 0.7,
            help="Level of public support for the bill"
        )
        factors['committee_approval'] = st.slider(
            "Committee Approval", 0.0, 1.0, 0.9,
            help="Level of support from relevant committees"
        )
        factors['fiscal_impact'] = st.slider(
            "Fiscal Impact", 0.0, 1.0, 0.6,
            help="Positive fiscal impact (0 = negative impact, 1 = positive impact)"
        )
        factors['urgency_factor'] = st.slider(
            "Urgency Factor", 0.0, 1.0, 0.8,
            help="How urgent is the bill (0 = not urgent, 1 = very urgent)"
        )
        factors['previous_similar_bills'] = st.slider(
            "Previous Similar Bills Success", 0.0, 1.0, 0.7,
            help="Success rate of similar bills in the past"
        )
        factors['media_coverage'] = st.slider(
            "Media Coverage", 0.0, 1.0, 0.6,
            help="Favorability of media coverage"
        )
    
    calculator = LegislativeCalculator()
    probability, breakdown = calculator.calculate_probability(factors)
    interpretation = calculator.get_interpretation(probability)
    
    with col2:
        st.subheader("Analysis Results")
        
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

if __name__ == "__main__":
    main()
