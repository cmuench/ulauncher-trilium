import re

import requests as req
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class TriliumExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def show_menu(self):
        items = []

        keyword = self.preferences["kw"]

        items.append(ExtensionResultItem(icon='images/trilium.png',
                                         name='Search note',
                                         description='Search Note ... (latest note on top)',
                                         on_enter=SetUserQueryAction("%s search " % keyword)))

        return RenderResultListAction(items)

    def get_server_url(self):
        return self.preferences["server_url"].strip("/")

    # Etapi GET request
    def request_etapi_get(self, path, query_params):
        headers = {
            "Authorization": self.preferences['api_token']
        }
        etapi_url = self.get_server_url() + "/etapi/" + path.strip("/") + "?" + query_params
        print(etapi_url)
        return req.get(etapi_url, headers=headers).json()

    def search_note(self, query):
        items = []

        if query:
            r = self.request_etapi_get(
                "/notes",
                "search=" + query.strip() + "&fastSearch=false&includeArchivedNotes=false&ancestorNoteId=root&ancestorDepth=2&orderBy=dateCreated&orderDirection=desc&limit=10&debug=false"
            )

            if 'results' in r:
                for row in r['results']:

                    items.append(ExtensionResultItem(icon='images/trilium.png',
                                                     name=row["title"],
                                                     description=row["dateCreated"],
                                                     on_enter=OpenUrlAction(self.get_server_url() + '/#root/' + row[
                                                         'noteId'])))

        return RenderResultListAction(items)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument() or ""

        if not query:
            return extension.show_menu()

        # Get the action based on the search terms
        search = re.findall(r"^search(.*)?$", query, re.IGNORECASE)

        if search:
            return extension.search_note(search[0])

        return HideWindowAction()


if __name__ == '__main__':
    TriliumExtension().run()

