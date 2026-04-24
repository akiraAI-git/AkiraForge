db = get_db_connection()
    cursor = db.cursor()

    try:
        print("[MIGRATION] Starting user_id default value fix...")

        cursor.execute("DESCRIBE generated_apps")
        columns = cursor.fetchall()

        user_id_column = None
        for col in columns:
            if col['Field'] == 'user_id':
                user_id_column = col
                break

        if not user_id_column:
            print("[MIGRATION] Column 'user_id' not found in generated_apps table")
            return False

        print(f"[MIGRATION] Current user_id definition: {user_id_column}")

        if user_id_column.get('Default') is not None:
            print(f"[MIGRATION] user_id already has default value: {user_id_column['Default']}")
            return True

        print("[MIGRATION] Adding default value to user_id...")
        cursor.execute("ALTER TABLE generated_apps MODIFY COLUMN user_id INT NOT NULL DEFAULT 1")
        db.commit()

        print("[MIGRATION]  Successfully fixed user_id default value!")
        return True

    except Exception as e:
        print(f"[MIGRATION]  Error: {e}")
        db.rollback()
        return False
    finally:
        cursor.close()

if __name__ == "__main__":
    print("=" * 70)
    print("AKIRA FORGE - DATABASE MIGRATION")
    print("Fixing user_id default value in generated_apps table")
    print("=" * 70)
    print()

    success = migrate_fix_user_id()

    print()
    if success:
        print(" Migration completed successfully!")
        print("You can now generate projects without errors.")
    else:
        print(" Migration failed. Check the error above.")
        print("You may need to run this SQL manually:")
        print("  ALTER TABLE generated_apps MODIFY COLUMN user_id INT NOT NULL DEFAULT 1;")

    print()
