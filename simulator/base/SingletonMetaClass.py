import threading

class SingletonMetaClass( type ):
	___lock = threading.Lock()
	___instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls.___instances:
	    		with cls.___lock:
	        		if cls not in cls.___instances:
            				cls.___instances[cls] = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
		return cls.___instances[cls]