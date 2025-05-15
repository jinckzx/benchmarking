        # if st.button("Select Metrics"):
        #     st.session_state.open_metrics_modal = True

        # # Create and configure the modal
        # metrics_modal = Modal(
        #     "Metrics Selection", 
        #     key="metrics_modal",
        #     padding=20,
        #     max_width=800
        # )
        #         # When the modal should be open
        # if st.session_state.open_metrics_modal:
        #     with metrics_modal.container():
        #         # Metrics selection section
        #         st.subheader("Metrics Selection")
                
        #         # Format available metrics for display
        #         metric_options = {name: metric.description for name, metric in available_metrics.items()}
                
        #         # Default to select all metrics if none are defined
        #         default_metrics = list(metric_options.keys()) if metric_options else []
        #         if not st.session_state.selected_metrics:
        #             default_selections = default_metrics[:2] if len(default_metrics) > 1 else default_metrics
        #         else:
        #             default_selections = st.session_state.selected_metrics
                    
        #         selected_metrics = st.multiselect(
        #             "Select Evaluation Metrics",
        #             options=list(metric_options.keys()),
        #             format_func=lambda x: f"{x} - {metric_options[x]}" if x in metric_options else x,
        #             default=default_selections,
        #             help="Select metrics to use for evaluation"
        #         )
                
        #         if not selected_metrics:
        #             st.warning("Please select at least one metric for evaluation")
                
        #         # Custom metric section toggle
        #         if st.button("➕ Add Custom Metric"):
        #             st.session_state.show_custom_metric_section = True
                
        #         # Custom metric section
        #         if st.session_state.show_custom_metric_section:
        #             st.markdown("### 🧩 Define Custom Metric")
                    
        #             # Start the form
        #             with st.form("custom_metric_form"):
        #                 # Render tabbed interface
        #                 render_custom_metric_tabs()
                        
        #                 # Save button
        #                 submit_button = st.form_submit_button("💾 Save Metric")
        #                 if submit_button:
        #                     try:
        #                         custom_code = st.session_state.sql_custom_metric_code
        #                         class_name = extract_class_name(custom_code)
        #                         file_path = save_custom_metric_to_file(custom_code, class_name)
        #                         register_custom_metric(file_path, class_name)
        #                         st.success(f"✅ Custom metric '{class_name}' saved and registered successfully!")
        #                     except Exception as e:
        #                         st.error(f"❌ Error saving metric: {e}")
                    
        #             if st.button("❌ Close Custom Metric Section"):
        #                 st.session_state.show_custom_metric_section = False
                
        #         # Modal footer with confirm/cancel buttons
        #         col1, col2, col3 = st.columns([1, 1, 1])
        #         with col2:
        #             if st.button("Confirm Selection"):
        #                 st.session_state.selected_metrics = selected_metrics
        #                 st.session_state.open_metrics_modal = False
        #                 st.rerun()
                
        #         with col3:
        #             if st.button("Cancel"):
        #                 st.session_state.open_metrics_modal = False
        #                 st.rerun()

        # # Display the currently selected metrics outside the modal
        # if st.session_state.selected_metrics:
        #     st.write("Selected metrics:", ", ".join(st.session_state.selected_metrics))