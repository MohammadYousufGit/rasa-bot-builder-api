

# Python and pip Installation


To use this Python project, you will need to have Python 3.10 and pip (the Python package manager) installed on your system.
# Rasa Installation
For Rasa framwork installation on your operating system please follow the documentation. Normally, you need to run following command.

```
sudo pip3 install rasa

```
## Add Rasa path to envirement
To add the Rasa path to the environment in Ubuntu, you can use the export command in the terminal.
First, navigate to the directory where Rasa is installed, and then use the following command as example to add the path: 

```
export PATH=$PATH:/path/to/rasa

```
Make sure to replace "/path/to/rasa" with the actual path to your Rasa installation.

You can also add this command to your .bashrc file so that it gets executed every time you open a new terminal. To do this, open the .bashrc file using a text editor, such as nano or vim, and add the export command to the end of the file. Then, save and close the file, and run the following command to update the environment:

```
source ~/.bashrc

```
This will add the Rasa path to the environment, and you should be able to use the Rasa command line interface (CLI) from any directory.

## Check version of netstat if installed 

After that, you should be able to use the Rasa CLI from any directory. You can test it by running the following command:


```
sudo rasa --version

```
# Libraries Installation


To install the required libraries for this project, navigate to the root directory of the project and run the following command:

```
pip install -r requirements.txt

```
if you run this API as root, you need to run following command

```
sudo pip3 install -r requirements.txt

```
This will install all of the necessary libraries specified in the requirements.txt file.

# Run the API


To run the project, navigate to the root directory of the project and run the following command:

```
python main.py

```

For some systems above command may not work. Need to run following command instead:


```
sudo python3 main.py

```
This will execute the main sever of the project.

# Note

Please note that this project may have additional dependencies or requirements, such as specific operating systems or hardware configurations. Be sure to consult the documentation or any accompanying README files for more information.
