ON DUPLICATE KEY UPDATE table_name = %s, column_name = %s""",
                (ai_id, table_name, column_name, table_name, column_name)
            )
            conn.commit()

            return (table_name, column_name)

        finally:
            cursor.close()

    @staticmethod
    def _get_available_table(cursor) -> str:
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        Data is stored as JSON in the AI's dedicated column.
        Returns empty dict if no data found.
            current_data = AIDataStore.retrieve_ai_data(ai_id, user_id)

            if not current_data:
                current_data = {
                    "ai_id": ai_id,
                    "user_id": user_id,
                    "interactions": [],
                    "preferences": {},
                    "metadata": {}
                }

            if "interactions" not in current_data:
                current_data["interactions"] = []

            interaction["timestamp"] = datetime.now().isoformat()
            current_data["interactions"].append(interaction)

            if len(current_data["interactions"]) > 1000:
                current_data["interactions"] = current_data["interactions"][-1000:]

            return AIDataStore.store_ai_data(ai_id, user_id, current_data)

        except Exception as e:
            print(f"[AI_DATA_STORE] Error appending interaction: {e}")
            return False

    @staticmethod
    def update_user_preferences(ai_id: str, user_id: int, preferences: dict) -> bool:
