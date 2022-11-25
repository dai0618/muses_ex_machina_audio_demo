from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

import threading
from typing import Any, Callable, Dict, List, Optional, Union

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from narator import text_to_speech


class OSCServer:
    def __init__(self, ip: str, port: int) -> None:
        # addresses
        self.address = "/read"
        self.address_hoge = "/example_hoge"
        self.address_fuga = "/example_fuga"
        self.address_piyo = "/example_piyo"
        # callback functions
        self.on_received: Optional[Callable] = None
        self.on_received_hoge: Optional[Callable] = None
        self.on_received_fuga: Optional[Callable] = None
        self.on_received_piyo: Optional[Callable] = None
        self.server: Optional[BlockingOSCUDPServer] = None
        self.ip = ip
        self.port = port

    def parse_message(self, input_args: str) -> List[str]:
        if type(input_args) == float:
            args = [input_args]
        else:
            args: List[str] = input_args.split(" ")
        return args

    def run(self, single_thread=False) -> None:
        """Start OSC server on main or sub thread.

        Args:
            single_thread (bool, optional): Defaults to False.
        """
        self.dispatcher = Dispatcher()

        if self.on_received:
            self.dispatcher.map(self.address,
                                self.on_received)  # type: ignore
        # NOTE: 受け付けるアドレスを増やしたい場合は以下のようにしてアドレスを増やす
        if self.on_received_hoge:
            self.dispatcher.map(self.address_hoge,
                                self.on_received_hoge)  # type: ignore
        if self.on_received_fuga:
            self.dispatcher.map(self.address_fuga,
                                self.on_received_fuga)  # type: ignore
        if self.on_received_piyo:
            self.dispatcher.map(self.address_piyo,
                                self.on_received_piyo)  # type: ignore

        self.server = BlockingOSCUDPServer(
            (self.ip, self.port), self.dispatcher)
        print(f"Serving on {self.server.server_address}")
        if single_thread:
            self.server.serve_forever()
        else:
            # running the server on new thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()

    def __del__(self):
        if self.server is not None:
            self.server.shutdown()


class OSCSender:
    def __init__(self, ip: str, port: int) -> None:
        self.client = udp_client.SimpleUDPClient(ip, port)
        # NOTE: 一つのSenderに付き送れるホストは一つ。
        self.ip = ip
        self.port = port

    def send(self, path: str, msg: Any) -> None:
        assert path[0] == "/", "given osc address path is incorrect"
        print(f"sending OSC message",
              f"(type={type(msg)})",
              f"to {self.ip}:{self.port}:{path}")
        self.client.send_message(path, msg)

    def __del__(self):
        if self.client is not None:
            del self.client


def get_sample_callback(sender: OSCSender, keyword: str = "") -> Callable:
    """Callback関数を返す関数

    Args:
        sender (OSCSender): 受信時にオウム返しをするのでClientのインスタンスが必要
        keyword (str, optional): hoge/fuga/piyo 等のアドレスのときどうするかみたいな.

    Returns:
        Callable: 関数を返す
    """

    # NOTE: もし機械学習モデル等を読む場合は、`get_sample_callback`の引数でパスを受け取り
    # ここでインスタンスの読み込みを行うことで、毎回の呼び出しでの読み込みなどが発生せずに済む
    # 例) model = Model.load_model(given_path)

    def callback_func(addr: str, *args: Any):
        """Actual callback function: 実際にOSCを受け取って呼ばれる関数

        Args:
            addr (str): OSCのパス (e.g. /path/to)
            args (Any): 可変長引数なのでTupleとして扱うこと
        """

        # NOTE: ここで処理を行う。
        # 例) res = model.generate(type=args[0])
        #     res.save_image("/generated/path.png")
        #     sender.send("/generated_result", "/generated/path.png")

        if keyword != "":
            print(keyword, "!!!!")
        print("received:", addr, args)
        
        #txtファイルを読み込んでaiffファイルに変換。
        text_file_path = args[0]
        if args[0].endswith(".txt"):
            text_file = open(text_file_path , 'r', encoding='UTF-8')
            text_data = text_file.read()
            print("prompt:", text_data)
            audio_file_path = text_to_speech(text_data)
        else:
            print("incorrect path:", args[0])
        
        address_state = "/finish_read"
        address_max= "/audio_path"
        sender.send(address_state,1) # state machine変換完了を送信。
        sender.send(address_max,audio_file_path)  # maxにaiffファイルのパスを送信。

    return callback_func


if __name__ == "__main__":
    server = OSCServer("127.0.0.1", 9999)
    sender = OSCSender("127.0.0.1", 8887)
    server.on_received = get_sample_callback(sender)
    # NOTE: 別のcallbackを用意しても良い
    # server.on_received_hoge = get_sample_callback(sender, "hoge")
    # server.on_received_fuga = get_sample_callback(sender, "fuga")
    # server.on_received_piyo = get_sample_callback(sender, "piyo")
    server.run(single_thread=True)