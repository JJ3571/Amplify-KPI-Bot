"""
Amplify KPI Calculator - Advanced scoring system matching Excel implementation
Includes sophisticated weighted scoring with conditional logic for missing metrics
"""

import pandas as pd
import numpy as np
from config import DEFAULT_WEIGHTS, METRIC_GOALS
from named_functions import NamedFunctions
import logging

class AmplifyKPICalculator:
    def __init__(self, agent_data, weights=None):
        """
        Initialize Amplify KPI Calculator
        
        Args:
            agent_data (pd.DataFrame): Merged agent data from exports
            weights (dict): Custom weights for KPI metrics. If None, uses defaults.
        """
        self.weights = weights or DEFAULT_WEIGHTS
        self.goals = METRIC_GOALS
        self.named_functions = NamedFunctions(agent_data)
        self.agent_data = agent_data
    
    def score_time_utilization(self, agent_name):
        """
        Calculate Time Utilization score - always 100% if agent has working hours
        Python equivalent of SCORE_TIME_UTILIZATION
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Score percentage (0-1)
        """
        working_hours = self.named_functions.working_hours(agent_name)
        return 1.0 if working_hours > 0 else 0.0
    
    def score_cases_per_hour(self, agent_name):
        """
        Calculate Cases Per Hour score percentage based on goal
        Python equivalent of SCORE_CPH
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Score percentage (0-1), capped at 100%
        """
        working_hours = self.named_functions.working_hours(agent_name)
        if working_hours <= 0:
            return 0.0
        
        cph = self.named_functions.cases_per_hour(agent_name)
        goal = self.goals['cases_per_hour']
        
        if cph == 0:
            return 0.0
        
        score = cph / goal
        return min(score, self.goals['max_score'])  # Cap at 100%
    
    def score_csat(self, agent_name):
        """
        Calculate CSAT score percentage based on goal
        Python equivalent of SCORE_CSAT
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Score percentage (0-1), capped at 100%
        """
        working_hours = self.named_functions.working_hours(agent_name)
        if working_hours <= 0:
            return 0.0
        
        csat = self.named_functions.csat_scores(agent_name)
        goal = self.goals['csat_score']
        
        # If no CSAT data, default to 100%
        if csat is None or csat == 1.0:
            return self.goals['max_score']
        
        score = csat / goal
        return min(score, self.goals['max_score'])  # Cap at 100%
    
    def score_initial_response(self, agent_name, response_type):
        """
        Calculate Initial Response score for chat/phone/email
        Python equivalent of SCORE_INITIAL_*_RESPONSE functions
        
        Args:
            agent_name (str): Agent name
            response_type (str): 'chat', 'phone', or 'email'
            
        Returns:
            float: Score percentage (0-1), None if no data
        """
        working_hours = self.named_functions.working_hours(agent_name)
        if working_hours <= 0:
            return 0.0
        
        # Get response time
        if response_type == 'chat':
            response_time = self.named_functions.initial_response_chat(agent_name)
            goal = self.goals['initial_chat']
        elif response_type == 'phone':
            response_time = self.named_functions.initial_response_phone(agent_name)
            goal = self.goals['initial_phone']
        elif response_type == 'email':
            response_time = self.named_functions.initial_response_email(agent_name)
            goal = self.goals['initial_email']
        else:
            return None
        
        # If no response time data, return None (will be handled in weighted calculation)
        if response_time is None or pd.isna(response_time):
            return None
        
        # Lower response time is better, so goal/response_time
        if response_time <= goal:
            return self.goals['max_score']  # 100% if under goal
        else:
            return goal / response_time  # Decreasing score for longer times
    
    def score_sla(self, agent_name):
        """
        Calculate SLA score based on percentage of cases out of SLA
        Python equivalent of SCORE_SLA
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Score percentage (0-1)
        """
        working_hours = self.named_functions.working_hours(agent_name)
        cases_closed = self.named_functions.cases_closed(agent_name)
        
        if working_hours <= 0 or cases_closed == 0:
            return 0.0
        
        sla_cases = self.named_functions.cases_out_of_sla(agent_name)
        max_allowed_sla = cases_closed * self.goals['sla_percentage']
        
        if sla_cases <= max_allowed_sla:
            return 1.0  # 100% if within SLA threshold
        else:
            return max_allowed_sla / sla_cases  # Decreasing score
    
    def score_qa(self, agent_name):
        """
        Calculate QA score percentage based on goal
        Python equivalent of SCORE_QA
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            float: Score percentage (0-1), capped at 100%
        """
        working_hours = self.named_functions.working_hours(agent_name)
        if working_hours <= 0:
            return 0.0
        
        qa_score = self.named_functions.qa_score(agent_name)
        goal = self.goals['qa_score']
        
        score = qa_score / goal
        return min(score, self.goals['max_score'])  # Cap at 100%
    
    def calculate_final_weighted_score(self, agent_name):
        """
        Calculate final weighted KPI score with sophisticated conditional logic
        Python equivalent of SCORE_FINAL_WEIGHTED
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            dict: All individual scores and final weighted score
        """
        working_hours = self.named_functions.working_hours(agent_name)
        
        # Return empty scores if no working hours
        if working_hours <= 0:
            return {
                'agent_name': agent_name,
                'working_hours': 0,
                'time_utilization_score': 0,
                'cph_score': 0,
                'csat_score': 0,
                'initial_chat_score': None,
                'initial_phone_score': None,
                'initial_email_score': None,
                'sla_score': 0,
                'qa_score': 0,
                'final_weighted_score': 0,
                'final_weighted_percentage': 0
            }
        
        # Calculate individual metric scores
        scores = {
            'agent_name': agent_name,
            'working_hours': working_hours,
            'time_utilization_score': self.score_time_utilization(agent_name),
            'cph_score': self.score_cases_per_hour(agent_name),
            'csat_score': self.score_csat(agent_name),
            'initial_chat_score': self.score_initial_response(agent_name, 'chat'),
            'initial_phone_score': self.score_initial_response(agent_name, 'phone'),
            'initial_email_score': self.score_initial_response(agent_name, 'email'),
            'sla_score': self.score_sla(agent_name),
            'qa_score': self.score_qa(agent_name)
        }
        
        # Calculate weighted score using complex conditional logic from Excel
        weighted_sum = 0.0
        
        # Time Utilization (always included if has working hours)
        weighted_sum += scores['time_utilization_score'] * self.weights['time_utilization']
        
        # Cases Per Hour
        weighted_sum += scores['cph_score'] * self.weights['cases_per_hour']
        
        # Initial Response Times - Complex conditional weighting
        chat_score = scores['initial_chat_score']
        phone_score = scores['initial_phone_score']
        email_score = scores['initial_email_score']
        
        # Count available response metrics
        available_responses = [s for s in [chat_score, phone_score, email_score] if s is not None]
        
        if len(available_responses) == 1:
            # Only one response type available - gets all response weight
            total_response_weight = (self.weights['initial_chat'] + 
                                   self.weights['initial_phone'] + 
                                   self.weights['initial_email'])
            
            if chat_score is not None:
                weighted_sum += chat_score * total_response_weight
            elif phone_score is not None:
                weighted_sum += phone_score * total_response_weight
            elif email_score is not None:
                weighted_sum += email_score * total_response_weight
                
        elif len(available_responses) == 2:
            # Two response types available - redistribute missing weight
            if chat_score is not None and phone_score is not None:
                # Chat and Phone available, Email missing
                weighted_sum += (chat_score * (self.weights['initial_chat'] + 
                                              self.weights['initial_email'] * 0.5))
                weighted_sum += (phone_score * (self.weights['initial_phone'] + 
                                               self.weights['initial_email'] * 0.5))
            elif chat_score is not None and email_score is not None:
                # Chat and Email available, Phone missing
                weighted_sum += (chat_score * (self.weights['initial_chat'] + 
                                              self.weights['initial_phone'] * 0.5))
                weighted_sum += (email_score * (self.weights['initial_email'] + 
                                               self.weights['initial_phone'] * 0.5))
            elif phone_score is not None and email_score is not None:
                # Phone and Email available, Chat missing
                weighted_sum += (phone_score * (self.weights['initial_phone'] + 
                                               self.weights['initial_chat'] * 0.5))
                weighted_sum += (email_score * (self.weights['initial_email'] + 
                                               self.weights['initial_chat'] * 0.5))
                
        elif len(available_responses) == 3:
            # All three response types available - use standard weights
            weighted_sum += chat_score * self.weights['initial_chat']
            weighted_sum += phone_score * self.weights['initial_phone']
            weighted_sum += email_score * self.weights['initial_email']
        
        # SLA Cases
        weighted_sum += scores['sla_score'] * self.weights['sla_cases']
        
        # QA Score
        weighted_sum += scores['qa_score'] * self.weights['qa_score']
        
        scores['final_weighted_score'] = weighted_sum
        scores['final_weighted_percentage'] = round(weighted_sum * 100, 2)
        
        return scores
    
    def get_performance_rating(self, score_percentage):
        """
        Get performance rating based on KPI score percentage
        
        Args:
            score_percentage (float): KPI score percentage (0-100)
            
        Returns:
            str: Performance rating
        """
        if score_percentage >= 90:
            return "Excellent"
        elif score_percentage >= 80:
            return "Good" 
        elif score_percentage >= 70:
            return "Average"
        elif score_percentage >= 60:
            return "Below Average"
        else:
            return "Needs Improvement"
    
    def calculate_all_agents(self):
        """
        Calculate KPIs for all agents in the dataset
        
        Returns:
            pd.DataFrame: DataFrame with all agent KPI calculations
        """
        results = []
        agent_names = self.agent_data['Name'].unique()
        
        logging.info(f"Calculating KPIs for {len(agent_names)} agents")
        
        for agent_name in agent_names:
            if pd.notna(agent_name) and agent_name.strip():
                agent_scores = self.calculate_final_weighted_score(agent_name)
                
                # Add raw metrics
                metrics = self.named_functions.get_agent_metrics(agent_name)
                agent_scores.update(metrics)
                
                # Add performance rating
                agent_scores['performance_rating'] = self.get_performance_rating(
                    agent_scores['final_weighted_percentage']
                )
                
                results.append(agent_scores)
        
        results_df = pd.DataFrame(results)
        
        # Filter out agents with no data
        results_df = results_df[results_df['working_hours'] > 0]
        
        logging.info(f"Completed KPI calculations for {len(results_df)} agents with data")
        
        return results_df
    
    def calculate_team_statistics(self, results_df):
        """
        Calculate team-level statistics
        
        Args:
            results_df (pd.DataFrame): Results from calculate_all_agents()
            
        Returns:
            dict: Team statistics
        """
        if results_df.empty:
            return {}
        
        stats = {
            'total_agents': len(results_df),
            'avg_kpi_score': results_df['final_weighted_percentage'].mean(),
            'median_kpi_score': results_df['final_weighted_percentage'].median(),
            'min_kpi_score': results_df['final_weighted_percentage'].min(),
            'max_kpi_score': results_df['final_weighted_percentage'].max(),
            'std_kpi_score': results_df['final_weighted_percentage'].std(),
        }
        
        # Performance distribution
        if 'performance_rating' in results_df.columns:
            performance_dist = results_df['performance_rating'].value_counts(normalize=True) * 100
            stats['performance_distribution'] = performance_dist.to_dict()
        
        # Average metrics
        metric_averages = {}
        metric_cols = ['time_utilization', 'cases_per_hour', 'qa_score', 
                      'working_hours', 'cases_closed', 'cases_transferred']
        
        for col in metric_cols:
            if col in results_df.columns:
                metric_averages[f'avg_{col}'] = results_df[col].mean()
        
        stats['metric_averages'] = metric_averages
        
        return stats
    
    def generate_agent_scorecard(self, agent_name):
        """
        Generate comprehensive scorecard matching the Excel format
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            dict: Complete agent scorecard data
        """
        # Get all scores and metrics
        scores = self.calculate_final_weighted_score(agent_name)
        metrics = self.named_functions.get_agent_metrics(agent_name)
        
        # Build scorecard matching Excel format
        scorecard = {
            'agent_breakdown': {
                'agent_name': agent_name,
                'time_utilization': f"{metrics['time_utilization']*100:.2f}%" if metrics['time_utilization'] else "0.00%",
                'working_hours': f"{metrics['working_hours']:.6f}" if metrics['working_hours'] else "0",
                'total_cases_closed': str(metrics['cases_closed']),
                'cases_worked_this_week': str(metrics['cases_transferred']),
                'cases_closed_plus_transferred': f"{metrics['cases_closed'] + metrics['cases_transferred']}",
                'cph': f"{metrics['cases_per_hour']:.3f}" if metrics['cases_per_hour'] else "0",
                'initial_chat_response': f"{metrics['initial_chat']:.1f}" if metrics['initial_chat'] is not None else "",
                'initial_phone_response': f"{metrics['initial_phone']:.0f}" if metrics['initial_phone'] is not None else "",
                'initial_email_response': f"{metrics['initial_email']:.0f}" if metrics['initial_email'] is not None else "",
                'cases_out_of_sla': str(metrics['cases_out_of_sla']),
                'qa_score': f"{metrics['qa_score']:.2f}" if metrics['qa_score'] else "100.00",
                'qa_bcf_percentage': f"{metrics['qa_bcf_percentage']*100:.2f}%" if metrics['qa_bcf_percentage'] else "0.00%",
                'qa_cases_audited': str(metrics['qa_cases_audited'])
            },
            'goal_comparison': {
                'time_utilization': {
                    'score_percentage': f"{scores['time_utilization_score']*100:.2f}%",
                    'goal': "90.00%",
                    'weight': "15.00%"
                },
                'cph': {
                    'score_percentage': f"{scores['cph_score']*100:.2f}%",
                    'goal': str(self.goals['cases_per_hour']),
                    'weight': "15.00%"
                },
                'initial_chat': {
                    'score_percentage': f"{scores['initial_chat_score']*100:.2f}%" if scores['initial_chat_score'] is not None else "",
                    'goal': str(int(self.goals['initial_chat'])),
                    'weight': "5.00%"
                },
                'initial_phone': {
                    'score_percentage': f"{scores['initial_phone_score']*100:.2f}%" if scores['initial_phone_score'] is not None else "",
                    'goal': str(int(self.goals['initial_phone'])),
                    'weight': "2.50%"
                },
                'initial_email': {
                    'score_percentage': f"{scores['initial_email_score']*100:.2f}%" if scores['initial_email_score'] is not None else "",
                    'goal': str(int(self.goals['initial_email'])),
                    'weight': "2.50%"
                },
                'cases_out_of_sla': {
                    'score_percentage': f"{scores['sla_score']*100:.2f}%",
                    'goal': "10.00%",
                    'weight': "10.00%"
                },
                'qa_score': {
                    'score_percentage': f"{scores['qa_score']*100:.2f}%",
                    'goal': str(self.goals['qa_score']),
                    'weight': "50.00%"
                }
            },
            'final_scores': {
                'final_weighted_score': f"{scores['final_weighted_percentage']:.2f}%",
                'kpi_gauge': f"{scores['final_weighted_percentage']:.2f}%",
                'performance_rating': self.get_performance_rating(scores['final_weighted_percentage'])
            },
            'qa_details': {
                'cases_audited': metrics['qa_cases_audited'],
                'bcf_percentage': metrics['qa_bcf_percentage'],
                'avg_score': metrics['qa_score']
            }
        }
        
        return scorecard
    
    def generate_recommendations(self, agent_name):
        """
        Generate improvement recommendations based on KPI scores
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            list: List of recommendations
        """
        scores = self.calculate_final_weighted_score(agent_name)
        recommendations = []
        
        # Check each metric against thresholds
        if scores['cph_score'] < 0.8:  # Less than 80%
            recommendations.append("Focus on improving case throughput - consider workflow optimization and time management")
        
        if scores['initial_chat_score'] is not None and scores['initial_chat_score'] < 0.8:
            recommendations.append("Work on reducing initial chat response time - aim for under 5 minutes")
        
        if scores['initial_phone_score'] is not None and scores['initial_phone_score'] < 0.8:
            recommendations.append("Improve phone response time - target under 60 seconds")
        
        if scores['initial_email_score'] is not None and scores['initial_email_score'] < 0.8:
            recommendations.append("Reduce email response time - aim for same-day responses")
        
        if scores['sla_score'] < 0.9:  # Less than 90%
            recommendations.append("Focus on SLA compliance - ensure timely case follow-up and resolution")
        
        if scores['qa_score'] < 0.9:  # Less than 90%
            recommendations.append("Review QA feedback and focus on quality improvement areas")
        
        # Overall performance recommendations
        final_score = scores['final_weighted_percentage']
        if final_score >= 90:
            recommendations.append("Excellent performance! Keep up the great work and consider mentoring other agents.")
        elif final_score >= 80:
            recommendations.append("Good performance overall. Focus on the specific areas noted above for improvement.")
        elif final_score >= 70:
            recommendations.append("Average performance. Prioritize the improvement areas and consider additional training.")
        else:
            recommendations.append("Performance below expectations. Work closely with your manager on an improvement plan.")
        
        return recommendations