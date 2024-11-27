import json
import pandas as pd
import streamlit as st

class CountryDataManager:
    def __init__(self, factbook_json_path):
        """Initialize with CIA World Factbook data"""
        with open(factbook_json_path, 'r', encoding='utf-8') as file:
            self.factbook_data = json.load(file)
        
        self.political_systems = self.extract_political_systems()
    
    def extract_political_systems(self):
        """Extract relevant political system information from Factbook data"""
        political_systems = {}
        
        for country_code, data in self.factbook_data.items():
            try:
                if 'Government' not in data:
                    continue
                    
                gov_data = data['Government']
                country_name = data.get('Government', {}).get('country_name', {}).get('conventional_long', '')
                
                political_systems[country_name] = {
                    'country_code': country_code,
                    'government_type': gov_data.get('government_type', ''),
                    'capital': gov_data.get('capital', {}).get('name', ''),
                    'executive_branch': {
                        'chief_of_state': gov_data.get('executive_branch', {}).get('chief_of_state', ''),
                        'head_of_government': gov_data.get('executive_branch', {}).get('head_of_government', ''),
                        'election_process': gov_data.get('executive_branch', {}).get('election_process', '')
                    },
                    'legislative_branch': {
                        'structure': gov_data.get('legislative_branch', {}).get('structure', ''),
                        'description': gov_data.get('legislative_branch', {}).get('description', ''),
                        'election_process': gov_data.get('legislative_branch', {}).get('election_process', '')
                    },
                    'judicial_branch': {
                        'highest_courts': gov_data.get('judicial_branch', {}).get('highest_courts', ''),
                        'selection_process': gov_data.get('judicial_branch', {}).get('selection_process', '')
                    },
                    'political_parties': gov_data.get('political_parties_and_leaders', {}),
                    'suffrage': gov_data.get('suffrage', ''),
                    'election_results': gov_data.get('election_results', {})
                }
                
                # Determine legislature type
                legislative_desc = str(gov_data.get('legislative_branch', {}).get('structure', '')).lower()
                if 'bicameral' in legislative_desc:
                    political_systems[country_name]['legislature_type'] = 'bicameral'
                elif 'unicameral' in legislative_desc:
                    political_systems[country_name]['legislature_type'] = 'unicameral'
                else:
                    political_systems[country_name]['legislature_type'] = 'unknown'
                
                # Determine system type
                gov_type = str(gov_data.get('government_type', '')).lower()
                if 'parliamentary' in gov_type:
                    political_systems[country_name]['system_type'] = 'parliamentary'
                elif 'presidential' in gov_type:
                    political_systems[country_name]['system_type'] = 'presidential'
                elif 'monarchy' in gov_type:
                    political_systems[country_name]['system_type'] = 'monarchy'
                else:
                    political_systems[country_name]['system_type'] = 'other'
                
            except Exception as e:
                print(f"Error processing {country_code}: {str(e)}")
                continue
        
        return political_systems
    
    def get_country_system(self, country_name):
        """Get political system details for a specific country"""
        return self.political_systems.get(country_name, None)
    
    def calculate_base_weights(self, country_name):
        """Calculate base weights based on country's political system"""
        country_data = self.get_country_system(country_name)
        if not country_data:
            return None
            
        weights = {
            'governing_party_support': 0.30,
            'opposition_support': 0.15,
            'public_opinion': 0.10,
            'committee_approval': 0.20,
            'fiscal_impact': 0.10,
            'urgency_factor': 0.05,
            'previous_similar_bills': 0.05,
            'media_coverage': 0.05
        }
        
        # Adjust weights based on system type
        if country_data['system_type'] == 'presidential':
            weights['governing_party_support'] = 0.25
            weights['opposition_support'] = 0.25
        elif country_data['system_type'] == 'monarchy':
            weights['governing_party_support'] = 0.25
            weights['public_opinion'] = 0.15
        
        # Adjust for legislature type
        if country_data['legislature_type'] == 'bicameral':
            # Reduce all weights proportionally to make room for chamber-specific weights
            for key in weights:
                weights[key] *= 0.7
            # Add chamber-specific weights
            weights['upper_house_support'] = 0.15
            weights['lower_house_support'] = 0.15
        
        return weights
    
    def get_all_country_names(self):
        """Get list of all countries in the database"""
        return sorted(self.political_systems.keys())

class LegislativeCalculatorEnhanced:
    def __init__(self, country_data_manager):
        self.data_manager = country_data_manager
    
    def calculate_probability(self, country_name, factors):
        """Calculate passage probability with country-specific adjustments"""
        base_weights = self.data_manager.calculate_base_weights(country_name)
        if not base_weights:
            return None, None
            
        country_system = self.data_manager.get_country_system(country_name)
        
        # Calculate weighted score
        total_score = 0
        breakdown = {}
        
        for factor, weight in base_weights.items():
            if factor in factors:
                score = factors[factor] * weight
                total_score += score
                breakdown[factor] = {
                    'raw_score': factors[factor],
                    'weight': weight,
                    'weighted_score': score
                }
        
        # Apply system-specific modifiers
        if country_system['system_type'] == 'monarchy':
            if factors.get('governing_party_support', 0) < 0.3:
                total_score *= 0.5
        
        final_probability = max(0, min(1, total_score))
        return final_probability, breakdown

def main():
    st.set_page_config(page_title="Enhanced Legislative Calculator", layout="wide")
    
    # Initialize data manager with CIA Factbook data
    data_manager = CountryDataManager('path_to_your_factbook.json')
    calculator = LegislativeCalculatorEnhanced(data_manager)
    
    # Rest of your Streamlit UI code...
    # Now using the enhanced calculator with CIA Factbook data