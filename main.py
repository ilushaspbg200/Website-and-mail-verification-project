import logic_of_work
from logic_of_work import logic

class main():
    while True:
        print("\n\n")
        if not logic.choosing_an_action():
            print("Работа окончена")
            break


if __name__ == "__main__":
    main()
