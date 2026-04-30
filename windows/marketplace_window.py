def __init__(self, username, callback_back_to_home=None):
        super().__init__()
        self.username = username
        self.callback_back_to_home = callback_back_to_home

        self.setWindowTitle(f"Akira Marketplace - {username}")
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1000, 600)

        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        title = QLabel(" Marketplace")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        top_layout.addWidget(title)

        back_btn = QPushButton("← Back to Home")
        back_btn.clicked.connect(self.go_back_home)
        back_btn.setMaximumWidth(120)
        top_layout.addWidget(back_btn)

        left_layout.addLayout(top_layout)

        left_layout.addWidget(QLabel("Search AIs:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self.search_ais)
        left_layout.addWidget(self.search_input)

        left_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All",
            "General",
            "Productivity",
            "Creative",
            "Analysis",
            "Coding",
            "Business"
        ])
        self.category_combo.currentTextChanged.connect(self.filter_category)
        left_layout.addWidget(self.category_combo)

        left_layout.addWidget(QLabel("Sort by:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Trending", "Highest Rated", "Newest"])
        self.sort_combo.currentTextChanged.connect(self.sort_ais)
        left_layout.addWidget(self.sort_combo)

        left_layout.addSpacing(20)

        left_layout.addWidget(QLabel("Your AIs:"))
        self.my_ais_list = QListWidget()
        left_layout.addWidget(self.my_ais_list)

        sell_btn = QPushButton("Sell Selected AI")
        sell_btn.clicked.connect(self.sell_ai)
        left_layout.addWidget(sell_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(250)

        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel("Available AIs:"))
        self.ai_list = QListWidget()
        self.ai_list.itemClicked.connect(self.show_ai_details)
        right_layout.addWidget(self.ai_list)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        right_layout.addWidget(self.details_text)

        btn_layout = QHBoxLayout()
        buy_btn = QPushButton("Download AI")
        buy_btn.clicked.connect(self.download_ai)
        btn_layout.addWidget(buy_btn)

        review_btn = QPushButton("Leave Review")
        review_btn.clicked.connect(self.leave_review)
        btn_layout.addWidget(review_btn)

        right_layout.addLayout(btn_layout)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        layout.addWidget(left_widget)
        layout.addWidget(right_widget, 1)

        main_widget.setLayout(layout)
        self.load_marketplace_data()

    def load_marketplace_data(self):
        ais = [
            {"name": "Email Assistant", "creator": "john_doe", "rating": 4.8, "downloads": 1250},
            {"name": "Code Generator", "creator": "dev_pro", "rating": 4.6, "downloads": 980},
            {"name": "Content Writer", "creator": "writer_ai", "rating": 4.9, "downloads": 2100},
        ]

        for ai in ais:
            item = QListWidgetItem(f"{ai['name']}  {ai['rating']}")
            self.ai_list.addItem(item)

    def search_ais(self):
        query = self.search_input.text()
        if query:
            QMessageBox.information(self, "Search", f"Searching for: {query}")

    def filter_category(self):
        category = self.category_combo.currentText()
        if category != "All":
            QMessageBox.information(self, "Filter", f"Showing {category} AIs")

    def sort_ais(self):
        sort_by = self.sort_combo.currentText()
        QMessageBox.information(self, "Sort", f"Sorted by: {sort_by}")

    def show_ai_details(self, item):
        self.details_text.setText("""
        AI Name: Email Assistant
        Creator: john_doe
        Rating:  (4.8/5)
        Downloads: 1,250
        Description: Helps you write and manage emails efficiently
        Features: AI writing, tone adjustment, templates
        License: Open Source (MIT)

    def leave_review(self):
        QMessageBox.information(self, "Review", "Review submitted!")

    def sell_ai(self):
        QMessageBox.information(self, "Sell", "AI listed in marketplace!")

    def go_back_home(self):
        if self.callback_back_to_home:
            self.callback_back_to_home()
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
            QLineEdit, QComboBox, QListWidget, QTextEdit {
                background-color: white;
                color: #1F2937;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
            }
