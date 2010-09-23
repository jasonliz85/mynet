
from django.core.management.base import LabelCommand

class Command(LabelCommand):
    def handle_label(self, label,**options):
        print 'Adding data from file: %s' % label
        f = opentextfile(label)
        if f:
            for line in f:
                line = line.strip()
                pass
            f.close()
        else:
            print 'File "%s" could not be opened' % label

