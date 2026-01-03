from fastapi import Request

from sandpiper.app.app import SandPiperApp


def get_sandpiper_app(request: Request) -> SandPiperApp:
    print("依存性注入: SandPiperAppを取得")
    return request.app.state.sandpiper_app  # type: ignore[no-any-return]
