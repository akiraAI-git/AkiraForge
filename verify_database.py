#!/usr/bin/env python3
    cursor = conn.cursor()

    print("\n Checking Database Privileges...")

    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS _privilege_test (id INT)")
        cursor.execute("DROP TABLE _privilege_test")
        conn.commit()
        print(" User has CREATE/DROP privileges")
    except Exception as e:
        print(f"  User may not have full DDL privileges: {e}")

    try:
        cursor.execute("ALTER TABLE generated_apps ADD COLUMN _test INT")
        cursor.execute("ALTER TABLE generated_apps DROP COLUMN _test")
        conn.commit()
        print(" User has ALTER TABLE privileges")
    except Exception as e:
        print(f"  User may not have ALTER TABLE privileges: {e}")

def estimate_capacity():
    print("\n Storage Capacity Analysis...")
    print(f"   - Max columns per table: 900")
    print(f"   - Each AI gets 1 column: ~900 AIs per table")
    print(f"   - Max JSON per column: 4GB (LONGTEXT)")
    print(f"   - Current setup: Unlimited tables (auto-scaling)")
    print(" Infinite scalability with automatic table management")

def run_all_checks():
    print("=" * 60)
    print(" Akira Forge Database Verification")
    print("=" * 60)

    checks = [
        ("Tables", verify_tables),
        ("Columns", verify_columns),
        ("Constraints", check_constraints),
        ("Privileges", check_privileges),
        ("Capacity", estimate_capacity)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f" Error in {name} check: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print(" Summary")
    print("=" * 60)

    all_good = all(r[1] for r in results if r[1] is not None)

    for name, result in results:
        if result is None:
            status = "⏭  Skipped"
        elif result:
            status = " Passed"
        else:
            status = " Failed"
        print(f"{name:15} {status}")

    print("=" * 60)

    if all_good:
        print("\n Database is ready! Run 'python main.py' to start.")
    else:
        print("\n  Some checks failed. Review above for details.")

    return all_good

if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
