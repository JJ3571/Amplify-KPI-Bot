"""
Named functions module - Python equivalents of Excel named functions
Converts complex Excel formulas to Python functions for KPI calculations
"""

import pandas as pd
import numpy as np
import logging
from config import METRIC_GOALS

class NamedFunctions:
    def __init__(self, agent_data):
        """
        Initialize with agent data
        
        Args:
            agent_data (pd.DataFrame): Merged agent data from exports
        """
        self.data = agent_data
        self.goals = METRIC_GOALS
        
    def cases_closed(self, agent_name):
        """
        Python equivalent of CASES_CLOSED named function
        Pulls # of cases closed from KPI Export
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            int: Number of cases closed
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0
            
            closed_cases = agent_row['closed_cases'].iloc[0] if 'closed_cases' in agent_row else 0
            return int(closed_cases) if pd.notna(closed_cases) else 0
        except KeyError as e:
            logging.warning(f"Missing column 'closed_cases' in data: {e}")
            return 0
        except Exception as e:
            logging.error(f"Error getting cases_closed for agent '{agent_name}': {e}")
            return 0
    
    def cases_transferred(self, agent_name):
        """
        Python equivalent of TRNSFR_CASES named function
        Pulls # of cases transferred to another team
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            int: Number of cases transferred
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0
            
            transferred_cases = agent_row['transferred_cases'].iloc[0] if 'transferred_cases' in agent_row else 0
            return int(transferred_cases) if pd.notna(transferred_cases) else 0
        except KeyError as e:
            logging.warning(f"Missing column 'transferred_cases' in data: {e}")
            return 0
        except Exception as e:
            logging.error(f"Error getting cases_transferred for agent '{agent_name}': {e}")
            return 0
    
    def cases_out_of_sla(self, agent_name):
        """
        Python equivalent of CASES_OUT_OF_SLA named function
        Totals Cases on the 3+ Day SLA report
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            int: Number of cases out of SLA
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0
            
            sla_cases = agent_row['sla_cases'].iloc[0] if 'sla_cases' in agent_row else 0
            return int(sla_cases) if pd.notna(sla_cases) else 0
        except KeyError as e:
            logging.warning(f"Missing column 'sla_cases' in data: {e}")
            return 0
        except Exception as e:
            logging.error(f"Error getting cases_out_of_sla for agent '{agent_name}': {e}")
            return 0
    
    def cases_per_hour(self, agent_name):
        """
        Python equivalent of CASES_PER_HOUR named function
        Calculates: (Cases Closed + Cases Transferred) / (Hrs Worked * Time Utilization %)
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Cases per hour
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0.0
            
            closed_cases = self.cases_closed(agent_name)
            transferred_cases = self.cases_transferred(agent_name)
            total_cases = closed_cases + transferred_cases
            
            working_hours = self.working_hours(agent_name)
            
            if working_hours > 0:
                cph = total_cases / working_hours
                return round(cph, 3)
            else:
                return 0.0
        except (ZeroDivisionError, ValueError) as e:
            logging.warning(f"Error calculating cases_per_hour for agent '{agent_name}': {e}")
            return 0.0
        except Exception as e:
            logging.error(f"Unexpected error in cases_per_hour for agent '{agent_name}': {e}")
            return 0.0
    
    def csat_scores(self, agent_name):
        """
        Python equivalent of CSAT_SCORES named function
        Calculates CSAT scores, treating 4-5 ratings as positive
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: CSAT percentage (0-1)
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found, defaulting CSAT to 100%")
                return 1.0  # Default to 100% if no CSAT data
            
            total_responses = agent_row['Total Responses'].iloc[0] if 'Total Responses' in agent_row else 0
            positive_responses = agent_row['Positive Responses'].iloc[0] if 'Positive Responses' in agent_row else 0
            
            if total_responses == 0:
                return 1.0  # No CSAT data = 100% (as per Excel logic)
            
            csat_rate = positive_responses / total_responses
            return round(csat_rate, 4)
        except (ZeroDivisionError, ValueError) as e:
            logging.warning(f"Error calculating CSAT for agent '{agent_name}': {e}")
            return 1.0
        except Exception as e:
            logging.error(f"Unexpected error in csat_scores for agent '{agent_name}': {e}")
            return 1.0
    
    def initial_response_chat(self, agent_name):
        """
        Python equivalent of INITIAL_RESPONSE_CHAT named function
        Pulls initial response time for chat
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Chat response time in minutes
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                return None
            
            chat_response = agent_row['chat_response_time'].iloc[0] if 'chat_response_time' in agent_row else None
            return float(chat_response) if pd.notna(chat_response) else None
        except (ValueError, TypeError) as e:
            logging.warning(f"Error converting chat_response_time for agent '{agent_name}': {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in initial_response_chat for agent '{agent_name}': {e}")
            return None
    
    def initial_response_email(self, agent_name):
        """
        Python equivalent of INITIAL_RESPONSE_EMAIL named function
        Pulls initial response time for email
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Email response time in minutes
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                return None
            
            email_response = agent_row['email_response_time'].iloc[0] if 'email_response_time' in agent_row else None
            return float(email_response) if pd.notna(email_response) else None
        except (ValueError, TypeError) as e:
            logging.warning(f"Error converting email_response_time for agent '{agent_name}': {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in initial_response_email for agent '{agent_name}': {e}")
            return None
    
    def initial_response_phone(self, agent_name):
        """
        Python equivalent of INITIAL_RESPONSE_PHONE named function
        Pulls initial response time for phone
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Phone response time in seconds
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                return None
            
            phone_response = agent_row['phone_response_time'].iloc[0] if 'phone_response_time' in agent_row else None
            return float(phone_response) if pd.notna(phone_response) else None
        except (ValueError, TypeError) as e:
            logging.warning(f"Error converting phone_response_time for agent '{agent_name}': {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in initial_response_phone for agent '{agent_name}': {e}")
            return None
    
    def time_utilization(self, agent_name):
        """
        Python equivalent of TIME_UTILIZATION named function
        Pulls agent Time Utilization % from KPI Export
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Time utilization percentage (0-1)
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0.0
            
            time_util = agent_row['Time Utilization Percent'].iloc[0] if 'Time Utilization Percent' in agent_row else 0.0
            return float(time_util) if pd.notna(time_util) else 0.0
        except KeyError as e:
            logging.warning(f"Missing column 'Time Utilization Percent' in data: {e}")
            return 0.0
        except Exception as e:
            logging.error(f"Error getting time_utilization for agent '{agent_name}': {e}")
            return 0.0
    
    def working_hours(self, agent_name):
        """
        Python equivalent of WORKING_HOURS named function
        Calculates agent total worked hours: (Total hours * Time utilization %)
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Working hours
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0.0
            
            total_hours = agent_row['Total Hours Worked'].iloc[0] if 'Total Hours Worked' in agent_row else 0.0
            time_util = self.time_utilization(agent_name)
            
            if pd.notna(total_hours) and pd.notna(time_util):
                working_hrs = float(total_hours) * float(time_util)
                return round(working_hrs, 6)
            else:
                return 0.0
        except (ValueError, TypeError) as e:
            logging.warning(f"Error calculating working_hours for agent '{agent_name}': {e}")
            return 0.0
        except Exception as e:
            logging.error(f"Unexpected error in working_hours for agent '{agent_name}': {e}")
            return 0.0
    
    def qa_bcf_percentage(self, agent_name):
        """
        Python equivalent of QA_BCF_PCNT named function
        Pulls agent BCF % from QA Export
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: BCF percentage (0-1)
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0.0
            
            bcf_pct = agent_row['bcf_percentage'].iloc[0] if 'bcf_percentage' in agent_row else 0.0
            return float(bcf_pct) if pd.notna(bcf_pct) else 0.0
        except KeyError as e:
            logging.warning(f"Missing column 'bcf_percentage' in data: {e}")
            return 0.0
        except Exception as e:
            logging.error(f"Error getting qa_bcf_percentage for agent '{agent_name}': {e}")
            return 0.0
    
    def qa_cases_audited(self, agent_name):
        """
        Python equivalent of QA_CASES_AUDITED named function
        Pulls # of agent cases audited from QA Export
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            int: Number of cases audited
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found in data")
                return 0
            
            cases_audited = agent_row['qa_cases_audited'].iloc[0] if 'qa_cases_audited' in agent_row else 0
            return int(cases_audited) if pd.notna(cases_audited) else 0
        except KeyError as e:
            logging.warning(f"Missing column 'qa_cases_audited' in data: {e}")
            return 0
        except Exception as e:
            logging.error(f"Error getting qa_cases_audited for agent '{agent_name}': {e}")
            return 0
    
    def qa_score(self, agent_name):
        """
        Python equivalent of QA_SCORE named function
        Pulls agent QA Score from QA Export
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: QA score (0-100)
        """
        try:
            agent_row = self.data[self.data['Name'] == agent_name]
            if agent_row.empty:
                logging.debug(f"Agent '{agent_name}' not found, defaulting QA score to 100")
                return 100.0  # Default to 100 if no QA data
            
            qa_score = agent_row['qa_score'].iloc[0] if 'qa_score' in agent_row else 100.0
            return float(qa_score) if pd.notna(qa_score) else 100.0
        except KeyError as e:
            logging.warning(f"Missing column 'qa_score' in data: {e}")
            return 100.0
        except Exception as e:
            logging.error(f"Error getting qa_score for agent '{agent_name}': {e}")
            return 100.0
    
    def get_agent_metrics(self, agent_name):
        """
        Get all metrics for an agent
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            dict: Dictionary with all agent metrics
        """
        working_hrs = self.working_hours(agent_name)
        
        # Only calculate metrics if agent has working hours
        if working_hrs == 0:
            return {
                'agent_name': agent_name,
                'working_hours': 0,
                'has_data': False
            }
        
        metrics = {
            'agent_name': agent_name,
            'working_hours': working_hrs,
            'has_data': True,
            'time_utilization': self.time_utilization(agent_name),
            'cases_closed': self.cases_closed(agent_name),
            'cases_transferred': self.cases_transferred(agent_name),
            'cases_per_hour': self.cases_per_hour(agent_name),
            'cases_out_of_sla': self.cases_out_of_sla(agent_name),
            'csat_score': self.csat_scores(agent_name),
            'initial_chat': self.initial_response_chat(agent_name),
            'initial_phone': self.initial_response_phone(agent_name),
            'initial_email': self.initial_response_email(agent_name),
            'qa_score': self.qa_score(agent_name),
            'qa_bcf_percentage': self.qa_bcf_percentage(agent_name),
            'qa_cases_audited': self.qa_cases_audited(agent_name)
        }
        
        return metrics