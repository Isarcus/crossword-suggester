import gui.suggester

gui.suggester.init()

try:
    while True:
        print("Enter query pattern:")
        req = input()
        gui.suggester.send_request(req)
        print("Press Enter to see the results!")
        input()
        results = gui.suggester.get_result()
        print(results)
except KeyboardInterrupt:
    pass
finally:
    print("Exiting")
    gui.suggester.shutdown()
