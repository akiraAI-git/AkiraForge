machine_uuid = DeviceLoginManager.get_machine_uuid()
            conn = get_db_connection()
            cursor = conn.cursor()

            token_data = f"{user_id}:{username}:{machine_uuid}:{datetime.now().isoformat()}"
            auth_token = hashlib.sha256(token_data.encode()).hexdigest()

            expires_at = datetime.now() + timedelta(days=remember_days)

            cursor.execute("""
                INSERT INTO device_logins (user_id, machine_uuid, auth_token, expires_at, device_name)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE auth_token = %s, expires_at = %s, last_accessed = NOW()
                cursor.close()

                if result:
                    return True, result["user_id"]

            return False, None
        except:
            return False, None

    @staticmethod
    def clear_device_login(username):
        try:
            machine_uuid = DeviceLoginManager.get_machine_uuid()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM device_logins WHERE machine_uuid = %s
            token_dir = Path.home() / ".akiraforge"
            token_dir.mkdir(parents=True, exist_ok=True)
            token_file = token_dir / f"{username}_token.json"

            with open(token_file, 'w') as f:
                json.dump({
                    "token": token,
                    "expires_at": expires_at.isoformat()
                }, f)
        except:
            pass

    @staticmethod
    def _get_local_token(username):
        try:
            token_file = Path.home() / ".akiraforge" / f"{username}_token.json"
            if token_file.exists():
                with open(token_file) as f:
                    return json.load(f)
        except:
            pass
        return None
