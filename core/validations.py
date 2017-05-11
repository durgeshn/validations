class Validations(object):
    _possibleStatus = ("WAITING", "RUNNING", "WARNING", "ERROR", "OK")
    _name = ""
    _category = ""

    def __init__(self, project):
        super(Validations, self).__init__()
        self.project = project
        self.errorLog = list()
        self.status = 'OK'
        self.errorMessage = ''
        self.errorNodes = list()
        self.miscData = None
        self.warningNodes = list()
        self.isFixable = True
        self.isNodes = True

    def _test(self):
        pass

    def setErrorMessage(self, errorMessage):
        self.errorMessage = errorMessage

    def setErrorLog(self, errorLog):
        self.errorLog.append(errorLog)

    def getErrorText(self):
        return '\n'.join(self.errorLog)

    def setErrorNodes(self, errorNodes=list()):
        self.errorNodes = errorNodes

    def setStatus(self, status):
        if status in self._possibleStatus:
            self.status = status
        else:
            raise RuntimeError('Invalid status change for %s' % self._name)

    def run(self):
        self.reset()
        self.outPut()

    def outPut(self):
        self.check()
        if self.status in ['ERROR', 'WARNING']:
            print '%s\t:-' % self._category
            print '%s\t:\t%s\n\t%s' % (self._name, self.status, self.errorMessage)
        elif self.status == 'OK':
            print self._category
            print '%s\t:\t%s' % (self._name, self.status)

    def check(self):
        pass

    def fix(self):
        pass

    def selectErrorNodes(self):
        pass

    def reset(self):
        self.errorLog = list()
        self.status = 'WAITING'
        self.errorMessage = ''
        self.errorNodes = list()

if __name__ == '__main__':
    val = Validations('bdg')
