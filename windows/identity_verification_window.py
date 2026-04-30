self,
            "Verification Started",
            "Opening Stripe Identity verification.\n\n"
            "You'll be redirected to a secure verification page where you can:\n"
            "1. Upload your government ID\n"
            "2. Verify your address\n"
            "3. Complete a liveness check (selfie)\n\n"
            "This typically takes 2-5 minutes."
        )

        result = self.verification_manager.initiate_seller_verification(
            self.user_id,
            "user@example.com",  # Get from actual user data
            self.username,
            phone="1234567890"
        )

        if result["success"]:
            self.status_text.setText(
                f"Verification Status: PENDING\n\n"
                f"Session ID: {result['session_id']}\n\n"
                "Please complete verification at:\n"
                f"{result['url']}\n\n"
                "After verification, check your status below."
            )

            self.progress.setValue(33)
            self.step1_check.setChecked(True)
            self.step1_check.setStyleSheet("color: #10B981;")

            check_btn = QPushButton("Check Verification Status")
            check_btn.clicked.connect(lambda: self.check_status(result['session_id']))
        else:
            QMessageBox.critical(self, "Error", f"Failed to start verification: {result['error']}")

    def check_status(self, session_id):
        result = self.verification_manager.service.check_verification_status(session_id)

        if result["success"]:
            if result["verified"]:
                QMessageBox.information(
                    self,
                    " Verified!",
                    "Your identity has been verified!\n\n"
                    "You can now:\n"
                    " List AI models on marketplace\n"
                    " Accept payments\n"
                    " Reach global audience"
                )
                self.progress.setValue(100)
                self.step2_check.setChecked(True)
                self.step3_check.setChecked(True)
                self.status_text.setText(
                    "Verification Status:  VERIFIED\n\n"
                    "Your identity has been successfully verified.\n"
                    "You now have full marketplace access."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Verification Pending",
                    "Your verification is still being processed.\n"
                    "Check again in a few moments."
                )
        else:
            QMessageBox.critical(self, "Error", f"Failed to check status: {result['error']}")

    def start_id_verification(self):
        QMessageBox.information(
            self,
            "Government ID Verification",
            "Please have a valid government-issued ID ready:\n\n"
            "Accepted:\n"
            " Passport\n"
            " Driver's License\n"
            " National ID Card\n\n"
            "Click 'Start Verification' to begin."
        )

    def start_address_verification(self):
        QMessageBox.information(
            self,
            "Address Verification",
            "Please have proof of address ready:\n\n"
            "Accepted:\n"
            " Utility bill\n"
            " Bank statement\n"
            " Government document\n\n"
            "Must be dated within last 3 months."
        )

    def start_liveness_verification(self):
        QMessageBox.information(
            self,
            "Liveness Check (Selfie)",
            "We'll need a photo of your face to confirm it's really you.\n\n"
            "Requirements:\n"
            " Good lighting\n"
            " Face clearly visible\n"
            " No filters or masks\n"
            " Camera functional"
        )

    def go_back(self):
        if self.callback_back:
            self.callback_back()
        self.close()

    def apply_theme(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F9FAFB;
            }
            QLabel {
                color: #1F2937;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QCheckBox {
                color: #1F2937;
                spacing: 5px;
            }
            QTextEdit {
                background-color: white;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 10px;
            }
