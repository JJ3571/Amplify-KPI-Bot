"""
Agent Scorecard Generator - Creates detailed scorecards matching Excel format
"""

import pandas as pd
import logging
from pathlib import Path

class ScorecardGenerator:
    def __init__(self, kpi_calculator):
        """
        Initialize scorecard generator
        
        Args:
            kpi_calculator (AmplifyKPICalculator): KPI calculator instance
        """
        self.calculator = kpi_calculator
    
    def generate_csv_scorecard(self, agent_name, output_path=None):
        """
        Generate CSV scorecard matching the Excel example format
        
        Args:
            agent_name (str): Agent name
            output_path (str): Optional output file path
            
        Returns:
            pd.DataFrame: Scorecard as DataFrame
        """
        scorecard_data = self.calculator.generate_agent_scorecard(agent_name)
        
        # Build CSV structure matching the Excel format
        rows = []
        
        # Header rows
        rows.append(['', '', '', '', '', '', '', ''])
        rows.append(['', 'Agent Breakdown', scorecard_data['agent_breakdown']['agent_name'], '', 'Team Averages', '', 'Department Averages', '', 'Additional Notes:'])
        
        # Agent metrics
        rows.append(['', 'Time Utilization', scorecard_data['agent_breakdown']['time_utilization'], '', '', '', '', ''])
        rows.append(['', 'Working Hours', scorecard_data['agent_breakdown']['working_hours'], '', '', '', '', ''])
        rows.append(['', 'Total Cases Closed', scorecard_data['agent_breakdown']['total_cases_closed'], '', '', '', '', ''])
        rows.append(['', 'Cases Worked This Week', scorecard_data['agent_breakdown']['cases_worked_this_week'], '', '', '', '', ''])
        rows.append(['', f"Cases [Clsd + Transf]    |   CPH", f"{scorecard_data['agent_breakdown']['cases_closed_plus_transferred']}  |  {scorecard_data['agent_breakdown']['cph']}", '', '', '', '', ''])
        rows.append(['', 'Initial Chat Response (Minutes)', scorecard_data['agent_breakdown']['initial_chat_response'], '', '', '', '', ''])
        rows.append(['', 'Initial Phone Response (Seconds)', scorecard_data['agent_breakdown']['initial_phone_response'], '', '', '', '', ''])
        rows.append(['', 'Initial Email Response (Minutes)', scorecard_data['agent_breakdown']['initial_email_response'], '', '', '', '', ''])
        rows.append(['', 'Cases out of SLA', scorecard_data['agent_breakdown']['cases_out_of_sla'], '', '', '', '', ''])
        rows.append(['', 'QA  - Score', scorecard_data['agent_breakdown']['qa_score'], '', '', '', '', ''])
        rows.append(['', 'QA - BCF %', scorecard_data['agent_breakdown']['qa_bcf_percentage'], '', '', '', '', ''])
        rows.append(['', 'QA - # of Cases Audited', scorecard_data['agent_breakdown']['qa_cases_audited'], '', '', '', '', ''])
        
        # Separator
        rows.append(['', '', '', '', '', '', '', ''])
        
        # Goal comparison header
        rows.append(['', 'How close to the Goal:', '', '', 'Goal/Expectation:', '', 'Each is worth __%', ''])
        rows.append(['', '= x / Goal %', '', '', '', '', '', ''])
        
        # Goal comparisons
        for metric, data in scorecard_data['goal_comparison'].items():
            metric_name = metric.replace('_', ' ').title()
            if metric == 'cph':
                metric_name = 'CPH'
            elif metric == 'qa_score':
                metric_name = 'QA  - Score'
            elif 'initial' in metric:
                if 'chat' in metric:
                    metric_name = 'Initial Chat Response (Minutes)'
                elif 'phone' in metric:
                    metric_name = 'Initial Phone Response (Seconds)'
                elif 'email' in metric:
                    metric_name = 'Initial Email Response (Minutes)'
            elif 'sla' in metric:
                metric_name = 'Cases out of SLA'
            
            rows.append(['', metric_name, data['score_percentage'], '', data['goal'], '', data['weight'], ''])
        
        # Separator
        rows.append(['', '', '', '', '', '', '', 'KPI Score Explanation'])
        
        # Final score
        rows.append(['', 'Final Weighted Score:', scorecard_data['final_scores']['final_weighted_score'], '', '', '', '', 'Link to Weekly Reflection'])
        rows.append(['', '', '', '', '', '', '', ''])
        rows.append(['', 'KPI Gauge', scorecard_data['final_scores']['kpi_gauge'], '', '', '', '', ''])
        
        # QA Details placeholder (would be filled from QA system)
        qa_rows = [
            ['', 'Case #', '', '', '', '', '', ''],
            ['', 'Sheet Name', '', '', '', '', '', ''],
            ['', 'Date', '', '', '', '', '', ''],
            ['', 'Agent Manager', '', '', '', '', '', ''],
            ['', 'Agent Name', '', '', '', '', '', ''],
            ['', 'Score', '', '', '', '', '', ''],
            ['', 'Salesforce Case Hyperlink', '', '', '', '', '', ''],
            ['', 'Intercom Chat URL', '', '', '', '', '', ''],
            ['', 'TalkDesk Call URL', '', '', '', '', '', ''],
            ['', 'Initial Response Time', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Greeting', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Contact/ Program Information', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Soft Skills', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Conversation Control', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Spelling & Grammar', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Gender Neutral Language', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Transfer and Hold', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Analytical Skills/Tools', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Email Structure', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Customer Education', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Accurate Service/Sub Issues', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Call Closure', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Subject', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Description', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Escalation Template', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Resolution Box (if applicable)', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Closing Procedure', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', 'Customer Follow-up Within SLA', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', 'Business Critical', '', '', '', '', ''],
            ['', '', 'Comments/Feedback', '', '', '', '', ''],
            ['', 'BCF Corrected', '', '', '', '', '', ''],
            ['', 'BCF Corrected Date', '', '', '', '', '', ''],
            ['', 'BCF Update Comment', '', '', '', '', '', '']
        ]
        
        rows.extend(qa_rows)
        
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Save to file if path provided
        if output_path:
            df.to_csv(output_path, index=False, header=False)
            logging.info(f"Scorecard saved to {output_path}")
        
        return df
    
    def generate_summary_scorecard(self, agent_name):
        """
        Generate a summary scorecard with key metrics only
        
        Args:
            agent_name (str): Agent name
            
        Returns:
            dict: Summary scorecard data
        """
        scorecard_data = self.calculator.generate_agent_scorecard(agent_name)
        
        summary = {
            'agent_name': agent_name,
            'final_kpi_score': scorecard_data['final_scores']['final_weighted_score'],
            'performance_rating': scorecard_data['final_scores']['performance_rating'],
            'time_utilization': scorecard_data['agent_breakdown']['time_utilization'],
            'cases_per_hour': scorecard_data['agent_breakdown']['cph'],
            'qa_score': scorecard_data['agent_breakdown']['qa_score'],
            'working_hours': scorecard_data['agent_breakdown']['working_hours'],
            'total_cases': scorecard_data['agent_breakdown']['cases_closed_plus_transferred'],
            'sla_cases': scorecard_data['agent_breakdown']['cases_out_of_sla'],
            'recommendations': self.calculator.generate_recommendations(agent_name)
        }
        
        return summary
    
    def generate_team_scorecards(self, output_folder="scorecards"):
        """
        Generate scorecards for all agents
        
        Args:
            output_folder (str): Folder to save individual scorecards
            
        Returns:
            dict: Summary of all generated scorecards
        """
        output_path = Path(output_folder)
        output_path.mkdir(exist_ok=True)
        
        agent_names = self.calculator.agent_data['Name'].unique()
        summaries = []
        
        for agent_name in agent_names:
            if pd.notna(agent_name) and agent_name.strip():
                # Check if agent has working hours
                working_hours = self.calculator.named_functions.working_hours(agent_name)
                
                if working_hours > 0:
                    # Generate full scorecard CSV
                    clean_name = "".join(c for c in agent_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{clean_name.replace(' ', '_')}_scorecard.csv"
                    file_path = output_path / filename
                    
                    self.generate_csv_scorecard(agent_name, str(file_path))
                    
                    # Generate summary
                    summary = self.generate_summary_scorecard(agent_name)
                    summary['scorecard_file'] = str(file_path)
                    summaries.append(summary)
        
        logging.info(f"Generated {len(summaries)} agent scorecards in {output_folder}")
        
        return {
            'total_agents': len(summaries),
            'output_folder': str(output_path),
            'agent_summaries': summaries
        }
    
    def create_team_summary_report(self, team_results):
        """
        Create a team summary report from all scorecards
        
        Args:
            team_results (dict): Results from generate_team_scorecards()
            
        Returns:
            pd.DataFrame: Team summary report
        """
        if not team_results['agent_summaries']:
            return pd.DataFrame()
        
        # Convert summaries to DataFrame
        summary_data = []
        for agent_summary in team_results['agent_summaries']:
            row = {
                'Agent Name': agent_summary['agent_name'],
                'KPI Score': agent_summary['final_kpi_score'],
                'Performance Rating': agent_summary['performance_rating'],
                'Time Utilization': agent_summary['time_utilization'],
                'Cases Per Hour': agent_summary['cases_per_hour'],
                'QA Score': agent_summary['qa_score'],
                'Working Hours': agent_summary['working_hours'],
                'Total Cases': agent_summary['total_cases'],
                'SLA Cases': agent_summary['sla_cases'],
                'Scorecard File': agent_summary['scorecard_file']
            }
            summary_data.append(row)
        
        df = pd.DataFrame(summary_data)
        
        # Sort by KPI score descending
        df['KPI Score Numeric'] = df['KPI Score'].str.replace('%', '').astype(float)
        df = df.sort_values('KPI Score Numeric', ascending=False)
        df = df.drop('KPI Score Numeric', axis=1)
        
        return df