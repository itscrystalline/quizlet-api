# calls quizlet.js and captures the output as JSON
# then parses the JSON and returns the data as a python dictionary

import json
import subprocess


def get_quizlet_data(quizlet_id: int) -> dict:
    """Calls quizlet.js and returns the data as a dictionary"""
    # call quizlet.js and capture the output as JSON
    output = subprocess.check_output(['node', 'quizlet.js', str(quizlet_id)])
    # parse the JSON and return the data as a dictionary
    return json.loads(output)


if __name__ == '__main__':
    # test the function
    print(get_quizlet_data(3013578))
