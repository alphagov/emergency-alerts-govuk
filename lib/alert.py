from lib.alert_date import AlertDate


class Alert:
    def __init__(self, dict_):
        for key, value in dict_.items():
            setattr(self, key, value)

        self.sent = AlertDate(self.sent)
        self.expires = AlertDate(self.expires)
