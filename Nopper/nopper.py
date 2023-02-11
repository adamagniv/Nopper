import openai
from time import sleep
from uuid import uuid4
from .nop_conn import NopConn

QUIT_MSG = 'NQUIT'
WELCOME = ("Hello, my name is Nopper. I'm inviting you to use this platform to try and have a conversation with my help.\n"
        "Please read the following rules before we begin.\n"
        "The Rules:\n"
        "\t1. You are going to have a conversation with the other person behind the blinds.\n"
        "\t2. You are NOT ALLOWED TO SPEAK OUTLOUD! use only the interface I provide you.\n"
        "\t3. I'll provide you with options to who you could talk to, you can choose any of them or by choosing OTHER.\n"
        "\t4. If you chose OTHER, I'll be able to generate any persona you'll want me to. Just make sure to be as descriptive as you can so I'll be able to get it right.\n"
        "\t5. You can talk about whatever you choose to. If you'll need an idea, I'll try to suggest something once we'll begin.\n"
        "\t6. If you want to quit please enter '" + QUIT_MSG + "' to shut me down.")

NOPPER_PERSONA = ["27 years old afro-american male rapper",
                  "wise 89 years old chinese buddhist monk",
                  "30 year old German female fashion designer"]

CHOICE_L = ["\t[1] " + NOPPER_PERSONA[0] + ".",
            "\t[2] " + NOPPER_PERSONA[1] + ".",
            "\t[3] " + NOPPER_PERSONA[2] + ".",
            "\t[4] other."]

CHOICE = "Please Choose a Persona to talk to [press the option's number]:\n" + "\n".join(x for x in CHOICE_L)

def print_banner():
    print("\nooooo      ooo                                                    ")
    print("`888b.     `8'                                                    ")
    print(" 8 `88b.    8   .ooooo.  oo.ooooo.  oo.ooooo.   .ooooo.  oooo d8b ")
    print(" 8   `88b.  8  d88' `88b  888' `88b  888' `88b d88' `88b `888""8P ")
    print(" 8     `88b.8  888   888  888   888  888   888 888ooo888  888     ")
    print(" 8       `888  888   888  888   888  888   888 888    .o  888     ")
    print("o8o        `8  `Y8bod8P'  888bod8P'  888bod8P' `Y8bod8P' d888b    ")
    print("                          888        888                          ")
    print("                         o888o      o888o                         \n")

    def loop_dots(msg):
        print(msg, end="", flush=True)
        for i in range(0, 3):
            sleep(0.7)
            print(".", end="", flush=True)
        print("", flush=True)
    loop_dots("WELCOME!\n\tInitializing")
    loop_dots("\tEstablishing Connection")
    loop_dots("\tWasting Your Time")
    print("", flush=True)

class Nopper:
    def __init__(self, nconn, key=None, log=True, is_master=False):
        self.nconn = nconn
        self.session = str(uuid4())
        self.is_master = is_master
        self.should_log = log
        self.log = ''
        self.persona = ''
        self.local_name = ''
        self.remote_name = ''
        self.gpt_engine = "text-davinci-003"
        openai.api_key = key

    def __del__(self):
        self.nconn.teardown()
        if (self.should_log) and (not self.log.closed):
            self.log.close()

    def create_log(self):
        log_path = ''
        if (self.is_master):
            self.nconn.NopSend(self.session)
            log_path = "conv_logs/" + self.session + "_master.txt"
        else:
            self.session = self.nconn.NopRecv().strip()
            log_path = "conv_logs/" + self.session + "_slave.txt"
        
        if (self.should_log):
            self.log = open(log_path, "w")

    def choose_persona(self):
        print(CHOICE)
        valid = False
        persona_choice = 0
        while (not valid):
            persona_choice = input("enter choice: ")
            try:
                persona_choice = int(persona_choice)
                if (persona_choice > len(CHOICE_L) or persona_choice == 0):
                    print("invalid option! try again.")
                    continue
            except:
                print("invalid option! please enter a number.")
                continue
            valid = True

        if persona_choice != len(CHOICE_L):
            self.persona = NOPPER_PERSONA[persona_choice - 1]
        else:
            self.persona = input("please describe the persona you would like to talk to:\n\t")
        
        print("Creating a Nopper as a " + self.persona + " for you to talk to.")
        self.local_name = input("last thing before we are done, please tell me your name: ").strip()
        self.nconn.NopSend(self.local_name)

        print("Now please wait while I'll check if your partner is ready to begin.")
        self.remote_name = self.nconn.NopRecv().strip()

        sleep(1.0)
        print("All set!")

        return True

    #def slave_wait(self):
    #    print(WAIT)
    #    scene_choice = int(self.nconn.NopRecv().strip())
    #    print("The other side chose scene: " + str(scene_choice))
    #    valid = False
    #    while(not valid):
    #        resp = input("Do you accept? [Y/N] : ").upper()
    #        if (resp != 'Y' and resp != 'N'):
    #            print("invalid option! try again")
    #            continue
    #        valid = True

    #    print("sending response to other side.")
    #    self.nconn.NopSend(resp)

    #    if (resp == 'Y'):
    #        self.set_scene(scene_choice)
    #        return True

    #    return False
    
    def create_gpt_response(self, text=''):
        completion = openai.Completion.create(engine=self.gpt_engine,
                                                prompt=text,
                                                temperature=0.7,
                                                max_tokens=96,
                                                top_p=1,
                                                frequency_penalty=0,
                                                presence_penalty=0)

        return completion.choices[0].text

    def rephrase_msg(self, orig_msg):
        rephrased_msg = orig_msg
        prompt = "rephrase the following sentence as a " + self.persona + " would have said it: " + orig_msg
        rephrased_msg = self.create_gpt_response(prompt).strip()
           
        return rephrased_msg
    
    def topic_example(self):
        prompt = "give me one example for a topic of conversation people might disagree about"
        return self.create_gpt_response(prompt).strip()

    def game(self):
        print(WELCOME)
        sleep(2)
        print("Let us begin.")
        self.choose_persona()

        # Starting Finally...
        quit = False
        if (self.is_master):
            topic = self.topic_example()
            print("You are starting the conversation.\nA topic for suggestion (you don't have to use it):\n" + topic)
            self.nconn.NopSend(topic)

            quit = not self.send_message()
            if quit:
                return
        else:
            topic = self.nconn.NopRecv().strip()
            print("Please wait for the other side to start the conversation.\nA topic for suggestion (you don't have to use it):\n" + topic)

        while (True):
            quit = not self.recv_message()
            if quit:
                break
            elif (self.is_master):
                print()
            
            quit = not self.send_message()
            if quit:
                break
            elif (not self.is_master):
                print()
        return

    def recv_message(self):
        msg = self.nconn.NopRecv()
        if msg == QUIT_MSG:
            print("[Nopper]: your partner shut me down. I will never understand humans...")
            return False

        rephrased_msg = self.rephrase_msg(msg)
        logged_msg = self.remote_name + ": " + rephrased_msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")
        print(logged_msg)

        return True

    def send_message(self):
        while (True):
            msg = input(self.local_name + ": ")
            if msg.strip() != '':
                break
            print("[Nopper]: psssssst, hey! write something!")

        logged_msg = self.local_name + ": " + msg
        if (self.should_log):
            self.log.write(logged_msg + "\n")

        quit = False
        if msg == QUIT_MSG:
            quit = True

        self.nconn.NopSend(msg)

        if quit:
            print("[Nopper]: I will never understand humans...")
            sleep(1)
            return False

        return True

    def run(self):
        self.nconn.setup()
        self.create_log()
        print_banner()
        self.game()

        return
