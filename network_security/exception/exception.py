import sys 
from ..logging.logger import logger


class network_security_exception(Exception):
    def __init__(self, error_message, error_detail:sys):
        # It's good practice to call the parent's __init__
        # We will format the detailed message here and pass it to the parent
        _,_,exc_tb = error_detail.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

        # The detailed message that will be the main message of this exception
        detailed_error_message = (
            f"Error occurred in python script [{file_name}] "
            f"at line number [{line_number}] with error message: {error_message}"
        )
        super().__init__(detailed_error_message)

if __name__ == "__main__":
    try:
        logger.info("Testing the network_security_exception class")
        a = 1/0
    except Exception as e:
        logger.info("Divide by zero error")
        raise network_security_exception(e, sys)    
    
