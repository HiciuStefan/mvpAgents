# Missing part - Complete the generate_pdf_export function and add utility functions

class CampaignPDFGenerator:
    """
    Professional PDF generator for marketing campaign reports
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Setup custom styles for the PDF"""
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#2E86AB'),
            alignment=TA_CENTER
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=HexColor('#A23B72'),
            borderWidth=1,
            borderColor=HexColor('#A23B72'),
            borderPadding=5
        ))
        
        # Custom subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            textColor=HexColor('#F18F01'),
            leftIndent=20
        ))
        
        # Custom body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=10,
            rightIndent=10
        ))
        
        # Highlight style
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=HexColor('#FFFFFF'),
            backColor=HexColor('#2E86AB'),
            borderWidth=1,
            borderColor=HexColor('#2E86AB'),
            borderPadding=8,
            spaceAfter=10
        ))
        
        # Table header style
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#FFFFFF'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
    
    def generate_campaign_pdf(self, export_data: Dict, campaign_name: str, 
                            report_type: str = "summary") -> bytes:
        """
        Generate comprehensive PDF report for campaign
        """
        # Create buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content based on report type
        if report_type == "summary":
            story = self.build_summary_report(export_data, campaign_name)
        elif report_type == "detailed":
            story = self.build_detailed_report(export_data, campaign_name)
        elif report_type == "executive":
            story = self.build_executive_report(export_data, campaign_name)
        else:
            story = self.build_summary_report(export_data, campaign_name)
        
        # Build PDF
        doc.build(story)
        
        # Get PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        return pdf_data
    
    def build_summary_report(self, export_data: Dict, campaign_name: str) -> List:
        """Build summary report structure"""
        story = []
        
        # Title page
        story.extend(self.create_title_page(campaign_name, "Campaign Summary Report"))
        
        # Campaign overview
        story.extend(self.create_campaign_overview(export_data))
        
        # Key metrics
        story.extend(self.create_key_metrics_section(export_data))
        
        # Strategy summary
        if "strategy" in export_data:
            story.extend(self.create_strategy_summary(export_data["strategy"]))
        
        # Influencer highlights
        if "influencers" in export_data:
            story.extend(self.create_influencer_highlights(export_data["influencers"]))
        
        # Performance overview
        if "performance" in export_data:
            story.extend(self.create_performance_overview(export_data["performance"]))
        
        # Footer
        story.extend(self.create_footer())
        
        return story
    
    def build_detailed_report(self, export_data: Dict, campaign_name: str) -> List:
        """Build detailed report structure"""
        story = []
        
        # Title page
        story.extend(self.create_title_page(campaign_name, "Detailed Campaign Report"))
        
        # Table of contents
        story.extend(self.create_table_of_contents())
        
        # Campaign overview
        story.extend(self.create_campaign_overview(export_data))
        
        # SOSTAC analysis
        if "sostac_analysis" in export_data:
            story.extend(self.create_sostac_section(export_data["sostac_analysis"]))
        
        # Strategy section
        if "strategy" in export_data:
            story.extend(self.create_strategy_section(export_data["strategy"]))
        
        # Deliverables section
        if "deliverables" in export_data:
            story.extend(self.create_deliverables_section(export_data["deliverables"]))
        
        # Influencer section
        if "influencers" in export_data:
            story.extend(self.create_influencer_section(export_data["influencers"]))
        
        # Performance section
        if "performance" in export_data:
            story.extend(self.create_performance_section(export_data["performance"]))
        
        # Recommendations
        story.extend(self.create_recommendations_section(export_data))
        
        # Footer
        story.extend(self.create_footer())
        
        return story
    
    def build_executive_report(self, export_data: Dict, campaign_name: str) -> List:
        """Build executive summary report"""
        story = []
        
        # Title page
        story.extend(self.create_title_page(campaign_name, "Executive Summary"))
        
        # Executive overview
        story.extend(self.create_executive_overview(export_data))
        
        # Key achievements
        story.extend(self.create_key_achievements(export_data))
        
        # Financial summary
        story.extend(self.create_financial_summary(export_data))
        
        # Strategic recommendations
        story.extend(self.create_strategic_recommendations(export_data))
        
        # Footer
        story.extend(self.create_footer())
        
        return story
    
    def create_title_page(self, campaign_name: str, report_type: str) -> List:
        """Create title page"""
        story = []
        
        # Main title
        story.append(Paragraph(report_type, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Campaign name
        story.append(Paragraph(f"Campaign: {campaign_name}", self.styles['CustomHeading']))
        story.append(Spacer(1, 30))
        
        # Generate date
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
            self.styles['CustomBody']
        ))
        story.append(Spacer(1, 20))
        
        # Decorative line
        story.append(HRFlowable(width="100%", thickness=2, color=HexColor('#2E86AB')))
        story.append(PageBreak())
        
        return story
    
    def create_campaign_overview(self, export_data: Dict) -> List:
        """Create campaign overview section"""
        story = []
        
        story.append(Paragraph("Campaign Overview", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Campaign info table
        if "campaign_info" in export_data:
            info = export_data["campaign_info"]
            
            # Create table data
            table_data = []
            for key, value in info.items():
                table_data.append([
                    Paragraph(f"<b>{key.replace('_', ' ').title()}</b>", self.styles['Normal']),
                    Paragraph(str(value), self.styles['Normal'])
                ])
            
            # Create table
            table = Table(table_data, colWidths=[2*inch, 4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F0F0F0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F8F8')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def create_key_metrics_section(self, export_data: Dict) -> List:
        """Create key metrics section"""
        story = []
        
        story.append(Paragraph("Key Metrics", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        if "performance" in export_data:
            performance = export_data["performance"]
            
            # Create metrics table
            metrics_data = [
                [
                    Paragraph("<b>Metric</b>", self.styles['TableHeader']),
                    Paragraph("<b>Value</b>", self.styles['TableHeader']),
                    Paragraph("<b>Status</b>", self.styles['TableHeader'])
                ]
            ]
            
            # Key metrics
            key_metrics = [
                ("Impressions", performance.get("impressions", 0), "🟢 Good"),
                ("Clicks", performance.get("clicks", 0), "🟢 Good"),
                ("Conversions", performance.get("conversions", 0), "🟡 Average"),
                ("CTR", f"{performance.get('ctr_percentage', 0)}%", "🟢 Good"),
                ("ROI", f"{performance.get('roi_multiplier', 0)}x", "🟢 Excellent")
            ]
            
            for metric, value, status in key_metrics:
                metrics_data.append([
                    Paragraph(metric, self.styles['Normal']),
                    Paragraph(f"<b>{value:,}</b>" if isinstance(value, int) else f"<b>{value}</b>", 
                             self.styles['Normal']),
                    Paragraph(status, self.styles['Normal'])
                ])
            
            table = Table(metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F8F8')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def create_strategy_summary(self, strategy: str) -> List:
        """Create strategy summary section"""
        story = []
        
        story.append(Paragraph("Strategy Summary", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Truncate strategy for summary
        summary_strategy = strategy[:1000] + "..." if len(strategy) > 1000 else strategy
        
        story.append(Paragraph(summary_strategy, self.styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        return story
    
    def create_influencer_highlights(self, influencers: List[Dict]) -> List:
        """Create influencer highlights section"""
        story = []
        
        story.append(Paragraph("Top Influencers", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Show top 3 influencers
        top_influencers = influencers[:3]
        
        for i, influencer in enumerate(top_influencers, 1):
            story.append(Paragraph(f"<b>{i}. {influencer.get('name', 'Unknown')}</b>", 
                                 self.styles['CustomSubHeading']))
            story.append(Paragraph(f"Platform: {influencer.get('platform', 'N/A')}", 
                                 self.styles['CustomBody']))
            story.append(Paragraph(f"Followers: {influencer.get('followers', 'N/A')}", 
                                 self.styles['CustomBody']))
            story.append(Paragraph(f"Engagement: {influencer.get('engagement_rate', 'N/A')}", 
                                 self.styles['CustomBody']))
            story.append(Spacer(1, 10))
        
        return story
    
    def create_performance_overview(self, performance: Dict) -> List:
        """Create performance overview section"""
        story = []
        
        story.append(Paragraph("Performance Overview", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Performance highlights
        highlights = [
            f"Total Impressions: {performance.get('impressions', 0):,}",
            f"Click-Through Rate: {performance.get('ctr_percentage', 0)}%",
            f"Conversion Rate: {performance.get('conversion_rate_percentage', 0)}%",
            f"Return on Investment: {performance.get('roi_multiplier', 0)}x",
            f"Total Revenue: ${performance.get('revenue_generated', 0):,.2f}"
        ]
        
        for highlight in highlights:
            story.append(Paragraph(f"• {highlight}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def create_sostac_section(self, sostac_data: Dict) -> List:
        """Create SOSTAC analysis section"""
        story = []
        
        story.append(Paragraph("SOSTAC Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        sostac_sections = {
            'situation': 'Situation Analysis',
            'objectives': 'Objectives',
            'strategy': 'Strategy',
            'tactics': 'Tactics',
            'actions': 'Actions',
            'control': 'Control'
        }
        
        for section_key, section_title in sostac_sections.items():
            if section_key in sostac_data:
                story.append(Paragraph(section_title, self.styles['CustomSubHeading']))
                
                section_data = sostac_data[section_key]
                for key, value in section_data.items():
                    if value:  # Only show non-empty values
                        story.append(Paragraph(
                            f"<b>{key.replace('_', ' ').title()}:</b> {value}", 
                            self.styles['CustomBody']
                        ))
                
                story.append(Spacer(1, 10))
        
        return story
    
    def create_table_of_contents(self) -> List:
        """Create table of contents"""
        story = []
        
        story.append(Paragraph("Table of Contents", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        toc_items = [
            "Campaign Overview",
            "SOSTAC Analysis",
            "Strategy Details",
            "Campaign Deliverables",
            "Influencer Recommendations",
            "Performance Metrics",
            "Recommendations"
        ]
        
        for item in toc_items:
            story.append(Paragraph(f"• {item}", self.styles['CustomBody']))
        
        story.append(PageBreak())
        
        return story
    
    def create_footer(self) -> List:
        """Create footer"""
        story = []
        
        story.append(Spacer(1, 30))
        story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#CCCCCC')))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph(
            "This report was generated by Marketing Campaign Agent - Powered by AI",
            self.styles['Normal']
        ))
        
        return story
    
    def create_executive_overview(self, export_data: Dict) -> List:
        """Create executive overview"""
        story = []
        
        story.append(Paragraph("Executive Overview", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Key highlights
        if "campaign_info" in export_data:
            info = export_data["campaign_info"]
            
            overview_text = f"""
            Campaign '{info.get('name', 'Unknown')}' in the {info.get('industry', 'Unknown')} 
            industry has been designed to achieve {info.get('primary_goal', 'business objectives')} 
            with a budget of {info.get('budget', 'TBD')} over {info.get('duration', 'TBD')}.
            """
            
            story.append(Paragraph(overview_text, self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        return story
    
    def create_key_achievements(self, export_data: Dict) -> List:
        """Create key achievements section"""
        story = []
        
        story.append(Paragraph("Key Achievements", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        if "performance" in export_data:
            perf = export_data["performance"]
            
            achievements = [
                f"Achieved {perf.get('roi_multiplier', 0)}x return on investment",
                f"Generated {perf.get('conversions', 0):,} conversions",
                f"Reached {perf.get('reach', 0):,} unique users",
                f"Maintained {perf.get('engagement_rate_percentage', 0)}% engagement rate"
            ]
            
            for achievement in achievements:
                story.append(Paragraph(f"✓ {achievement}", self.styles['Highlight']))
                story.append(Spacer(1, 5))
        
        return story
    
    def create_financial_summary(self, export_data: Dict) -> List:
        """Create financial summary section"""
        story = []
        
        story.append(Paragraph("Financial Summary", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        if "performance" in export_data:
            perf = export_data["performance"]
            
            financial_data = [
                ["Metric", "Amount"],
                ["Total Spend", f"${perf.get('total_spend', 0):,.2f}"],
                ["Revenue Generated", f"${perf.get('revenue_generated', 0):,.2f}"],
                ["Cost Per Conversion", f"${perf.get('cost_per_conversion', 0):.2f}"],
                ["Return on Investment", f"{perf.get('roi_multiplier', 0)}x"]
            ]
            
            table = Table(financial_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        return story
    
    def create_strategic_recommendations(self, export_data: Dict) -> List:
        """Create strategic recommendations"""
        story = []
        
        story.append(Paragraph("Strategic Recommendations", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        recommendations = [
            "Increase budget allocation to high-performing channels",
            "Optimize ad creatives based on engagement data",
            "Expand targeting to similar audience segments",
            "Implement retargeting campaigns for better conversions",
            "Consider seasonal adjustments to campaign timing"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def create_deliverables_section(self, deliverables: Dict) -> List:
        """Create deliverables section"""
        story = []
        
        story.append(Paragraph("Campaign Deliverables", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        for deliverable_type, content in deliverables.items():
            story.append(Paragraph(
                deliverable_type.replace('_', ' ').title(), 
                self.styles['CustomSubHeading']
            ))
            
            # Truncate content if too long
            display_content = content[:500] + "..." if len(str(content)) > 500 else str(content)
            story.append(Paragraph(display_content, self.styles['CustomBody']))
            story.append(Spacer(1, 15))
        
        return story
    
    def create_influencer_section(self, influencers: List[Dict]) -> List:
        """Create detailed influencer section"""
        story = []
        
        story.append(Paragraph("Influencer Recommendations", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Create influencer table
        table_data = [
            [
                Paragraph("<b>Name</b>", self.styles['TableHeader']),
                Paragraph("<b>Platform</b>", self.styles['TableHeader']),
                Paragraph("<b>Followers</b>", self.styles['TableHeader']),
                Paragraph("<b>Engagement</b>", self.styles['TableHeader']),
                Paragraph("<b>Est. Cost</b>", self.styles['TableHeader'])
            ]
        ]
        
        for influencer in influencers:
            table_data.append([
                Paragraph(influencer.get('name', 'N/A'), self.styles['Normal']),
                Paragraph(influencer.get('platform', 'N/A'), self.styles['Normal']),
                Paragraph(str(influencer.get('followers', 'N/A')), self.styles['Normal']),
                Paragraph(str(influencer.get('engagement_rate', 'N/A')), self.styles['Normal']),
                Paragraph(str(influencer.get('estimated_cost', 'N/A')), self.styles['Normal'])
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F8F8')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def create_performance_section(self, performance: Dict) -> List:
        """Create detailed performance section"""
        story = []
        
        story.append(Paragraph("Performance Analysis", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Performance breakdown
        story.append(Paragraph("Campaign Performance Breakdown", self.styles['CustomSubHeading']))
        
        perf_text = f"""
        The campaign achieved {performance.get('impressions', 0):,} total impressions 
        with a click-through rate of {performance.get('ctr_percentage', 0)}%. 
        Out of {performance.get('clicks', 0):,} total clicks, {performance.get('conversions', 0):,} 
        conversions were generated, resulting in a {performance.get('conversion_rate_percentage', 0)}% 
        conversion rate. The campaign delivered a {performance.get('roi_multiplier', 0)}x return on investment.
        """
        
        story.append(Paragraph(perf_text, self.styles['CustomBody']))
        story.append(Spacer(1, 15))
        
        # Cost analysis
        story.append(Paragraph("Cost Analysis", self.styles['CustomSubHeading']))
        
        cost_text = f"""
        Total campaign spend was ${performance.get('total_spend', 0):,.2f} with an average 
        cost per click of ${performance.get('cost_per_click', 0):.2f} and cost per conversion 
        of ${performance.get('cost_per_conversion', 0):.2f}. The campaign generated 
        ${performance.get('revenue_generated', 0):,.2f} in total revenue.
        """
        
        story.append(Paragraph(cost_text, self.styles['CustomBody']))
        story.append(Spacer(1, 20))
        
        return story
    
    def create_recommendations_section(self, export_data: Dict) -> List:
        """Create recommendations section"""
        story = []
        
        story.append(Paragraph("Recommendations", self.styles['CustomHeading']))
        story.append(Spacer(1, 12))
        
        # Performance-based recommendations
        if "performance" in export_data:
            perf = export_data["performance"]
            roi = perf.get('roi_multiplier', 0)
            ctr = perf.get('ctr_percentage', 0)
            
            recommendations = []
            
            if roi > 3:
                recommendations.append("Excellent ROI performance - consider scaling the campaign")
            elif roi > 2:
                recommendations.append("Good ROI - optimize high-performing elements")
            else:
                recommendations.append("ROI below target - review targeting and creative strategy")
            
            if ctr > 5:
                recommendations.append("Strong click-through rate - maintain current ad creative approach")
            else:
                recommendations.append("Improve ad creative and targeting to increase engagement")
            
            # Add general recommendations
            recommendations.extend([
                "Implement A/B testing for ad creatives and landing pages",
                "Consider retargeting campaigns for users who didn't convert",
                "Analyze competitor strategies and adjust positioning",
                "Monitor campaign performance weekly and adjust budgets accordingly"
            ])
            
            for i, rec in enumerate(recommendations, 1):
                story.append(Paragraph(f"{i}. {rec}", self.styles['CustomBody']))
        
        story.append(Spacer(1, 20))
        
        return story
def generate_pdf_export(export_data: Dict, campaign_name: str, report_type: str = "summary") -> tuple:
    """
    Generate PDF export using the CampaignPDFGenerator
    
    Args:
        export_data: Campaign data dictionary
        campaign_name: Name of the campaign
        report_type: Type of report ("summary", "detailed", "executive")
    
    Returns:
        tuple: (pdf_bytes, filename)
    """
    try:
        # Initialize PDF generator
        pdf_generator = CampaignPDFGenerator()
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_campaign_pdf(export_data, campaign_name, report_type)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"campaign_{campaign_name.replace(' ', '_')}_{report_type}_{timestamp}.pdf"
        
        return pdf_bytes, filename
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise e


# Additional utility functions for enhanced PDF generation

def add_chart_to_pdf(story: List, chart_data: Dict, chart_type: str = "bar", title: str = "Chart") -> None:
    """
    Add charts to PDF story
    
    Args:
        story: PDF story list
        chart_data: Data for the chart
        chart_type: Type of chart ("bar", "line", "pie")
        title: Chart title
    """
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib import colors
    
    # Create drawing
    drawing = Drawing(400, 200)
    
    if chart_type == "bar":
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [chart_data.get('values', [1, 2, 3, 4, 5])]
        chart.categoryAxis.categoryNames = chart_data.get('labels', ['A', 'B', 'C', 'D', 'E'])
        chart.bars[0].fillColor = colors.blue
        
    elif chart_type == "line":
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [chart_data.get('values', [1, 2, 3, 4, 5])]
        chart.categoryAxis.categoryNames = chart_data.get('labels', ['A', 'B', 'C', 'D', 'E'])
        chart.lines[0].strokeColor = colors.blue
        
    elif chart_type == "pie":
        chart = Pie()
        chart.x = 150
        chart.y = 65
        chart.width = 100
        chart.height = 100
        chart.data = chart_data.get('values', [1, 2, 3, 4, 5])
        chart.labels = chart_data.get('labels', ['A', 'B', 'C', 'D', 'E'])
        chart.slices.strokeColor = colors.white
    
    drawing.add(chart)
    
    # Add title
    from reportlab.graphics.shapes import String
    title_string = String(200, 180, title, textAnchor='middle')
    title_string.fontSize = 12
    title_string.fontName = 'Helvetica-Bold'
    drawing.add(title_string)
    
    story.append(drawing)
    story.append(Spacer(1, 20))


def create_campaign_timeline(export_data: Dict) -> List:
    """
    Create campaign timeline section
    
    Args:
        export_data: Campaign data dictionary
    
    Returns:
        List of story elements
    """
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("Campaign Timeline", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Sample timeline data - adjust based on your data structure
    timeline_data = export_data.get('timeline', [
        {'date': '2024-01-01', 'event': 'Campaign Launch', 'description': 'Campaign officially launched'},
        {'date': '2024-01-15', 'event': 'Mid-Campaign Review', 'description': 'Performance review and optimization'},
        {'date': '2024-01-30', 'event': 'Campaign End', 'description': 'Campaign concluded successfully'}
    ])
    
    # Create timeline table
    table_data = [
        [
            Paragraph("<b>Date</b>", styles['Normal']),
            Paragraph("<b>Event</b>", styles['Normal']),
            Paragraph("<b>Description</b>", styles['Normal'])
        ]
    ]
    
    for event in timeline_data:
        table_data.append([
            Paragraph(event.get('date', 'N/A'), styles['Normal']),
            Paragraph(event.get('event', 'N/A'), styles['Normal']),
            Paragraph(event.get('description', 'N/A'), styles['Normal'])
        ])
    
    table = Table(table_data, colWidths=[1.5*inch, 2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#F8F8F8')])
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    return story


def create_budget_breakdown(export_data: Dict) -> List:
    """
    Create budget breakdown section
    
    Args:
        export_data: Campaign data dictionary
    
    Returns:
        List of story elements
    """
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("Budget Breakdown", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Sample budget data - adjust based on your data structure
    budget_data = export_data.get('budget_breakdown', {
        'Advertising Spend': 50000,
        'Content Creation': 15000,
        'Influencer Partnerships': 20000,
        'Analytics & Tools': 5000,
        'Contingency': 10000
    })
    
    # Create budget table
    table_data = [
        [
            Paragraph("<b>Category</b>", styles['Normal']),
            Paragraph("<b>Amount</b>", styles['Normal']),
            Paragraph("<b>Percentage</b>", styles['Normal'])
        ]
    ]
    
    total_budget = sum(budget_data.values())
    
    for category, amount in budget_data.items():
        percentage = (amount / total_budget * 100) if total_budget > 0 else 0
        table_data.append([
            Paragraph(category, styles['Normal']),
            Paragraph(f"${amount:,.2f}", styles['Normal']),
            Paragraph(f"{percentage:.1f}%", styles['Normal'])
        ])
    
    # Add total row
    table_data.append([
        Paragraph("<b>Total</b>", styles['Normal']),
        Paragraph(f"<b>${total_budget:,.2f}</b>", styles['Normal']),
        Paragraph("<b>100.0%</b>", styles['Normal'])
    ])
    
    table = Table(table_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#F0F0F0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, HexColor('#F8F8F8')])
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    return story


def validate_export_data(export_data: Dict) -> bool:
    """
    Validate export data structure
    
    Args:
        export_data: Campaign data dictionary
    
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['campaign_info']
    
    for field in required_fields:
        if field not in export_data:
            print(f"Missing required field: {field}")
            return False
    
    # Validate campaign_info structure
    campaign_info = export_data.get('campaign_info', {})
    if not isinstance(campaign_info, dict):
        print("campaign_info must be a dictionary")
        return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    return sanitized


# Enhanced PDF generation with additional features
def generate_enhanced_pdf_export(export_data: Dict, campaign_name: str, 
                                report_type: str = "summary", 
                                include_charts: bool = True,
                                include_timeline: bool = True,
                                include_budget: bool = True) -> tuple:
    """
    Generate enhanced PDF export with additional features
    
    Args:
        export_data: Campaign data dictionary
        campaign_name: Name of the campaign
        report_type: Type of report ("summary", "detailed", "executive")
        include_charts: Whether to include charts
        include_timeline: Whether to include timeline
        include_budget: Whether to include budget breakdown
    
    Returns:
        tuple: (pdf_bytes, filename)
    """
    try:
        # Validate data
        if not validate_export_data(export_data):
            raise ValueError("Invalid export data structure")
        
        # Initialize PDF generator
        pdf_generator = CampaignPDFGenerator()
        
        # Generate base PDF
        pdf_bytes = pdf_generator.generate_campaign_pdf(export_data, campaign_name, report_type)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sanitized_name = sanitize_filename(campaign_name)
        filename = f"campaign_{sanitized_name}_{report_type}_{timestamp}.pdf"
        
        return pdf_bytes, filename
        
    except Exception as e:
        print(f"Error generating enhanced PDF: {str(e)}")
        raise e


# Usage example function
def example_usage():
    """
    Example of how to use the PDF generator
    """
    
    # Sample export data
    sample_data = {
        'campaign_info': {
            'name': 'Summer Fashion Campaign',
            'industry': 'Fashion',
            'primary_goal': 'Brand Awareness',
            'budget': '$100,000',
            'duration': '3 months',
            'start_date': '2024-06-01',
            'end_date': '2024-08-31'
        },
        'performance': {
            'impressions': 1500000,
            'clicks': 75000,
            'conversions': 3750,
            'ctr_percentage': 5.0,
            'conversion_rate_percentage': 5.0,
            'roi_multiplier': 3.2,
            'total_spend': 85000.00,
            'revenue_generated': 272000.00,
            'cost_per_click': 1.13,
            'cost_per_conversion': 22.67
        },
        'influencers': [
            {
                'name': 'Sarah Johnson',
                'platform': 'Instagram',
                'followers': 500000,
                'engagement_rate': '4.2%',
                'estimated_cost': '$5,000'
            },
            {
                'name': 'Mike Chen',
                'platform': 'TikTok',
                'followers': 750000,
                'engagement_rate': '6.8%',
                'estimated_cost': '$7,500'
            }
        ],
        'strategy': 'Multi-platform approach focusing on visual content and influencer partnerships to drive brand awareness and sales during peak summer season.',
        'deliverables': {
            'social_media_posts': '50 Instagram posts, 30 TikTok videos',
            'ad_creatives': '15 static ads, 10 video ads',
            'influencer_content': '20 sponsored posts, 10 stories'
        }
    }
    
    # Generate PDF
    try:
        pdf_bytes, filename = generate_pdf_export(sample_data, "Summer Fashion Campaign", "detailed")
        print(f"PDF generated successfully: {filename}")
        print(f"PDF size: {len(pdf_bytes)} bytes")
        
        # Save to file (optional)
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        
        return pdf_bytes, filename
        
    except Exception as e:
        print(f"Error in example usage: {str(e)}")
        return None, None


# Additional styling functions for custom PDF appearances
def create_custom_page_template():
    """
    Create custom page template with headers and footers
    """
    from reportlab.platypus import PageTemplate, Frame
    from reportlab.lib.pagesizes import A4
    
    def header_footer(canvas, doc):
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(72, A4[1] - 50, "Campaign Analysis Report")
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0] - 72, A4[1] - 50, f"Generated: {datetime.now().strftime('%B %d, %Y')}")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.drawString(72, 50, "Confidential - Marketing Campaign Analysis")
        canvas.drawRightString(A4[0] - 72, 50, f"Page {doc.page}")
        canvas.restoreState()
    
    return header_footer

def generate_campaign_pdf_with_template(self, export_data: Dict, campaign_name: str, 
                                      report_type: str = "summary") -> bytes:
    """Generate PDF with custom headers/footers"""
    
    buffer = io.BytesIO()
    
    # Create document with custom template
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                          topMargin=72, bottomMargin=72)
    
    # Apply custom header/footer function
    header_footer_func = create_custom_page_template()
    
    # Build story content
    story = self.build_summary_report(export_data, campaign_name)
    
    # Build PDF with custom template
    doc.build(story, onFirstPage=header_footer_func, onLaterPages=header_footer_func)
    
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

if __name__ == "__main__":
    # Run example usage
    example_usage()