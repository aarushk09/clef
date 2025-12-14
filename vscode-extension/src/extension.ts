import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';

let outputChannel: vscode.OutputChannel;
let diagnosticCollection: vscode.DiagnosticCollection;

export function activate(context: vscode.ExtensionContext) {
    outputChannel = vscode.window.createOutputChannel('Clef');
    diagnosticCollection = vscode.languages.createDiagnosticCollection('clef');
    
    context.subscriptions.push(outputChannel);
    context.subscriptions.push(diagnosticCollection);
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('clef.run', runScore)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('clef.validate', validateScore)
    );
    
    context.subscriptions.push(
        vscode.commands.registerCommand('clef.build', buildScore)
    );
    
    // Validate on save if enabled
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument((document) => {
            if (document.languageId === 'clef') {
                const config = vscode.workspace.getConfiguration('clef');
                if (config.get('validateOnSave', true)) {
                    validateDocument(document);
                }
            }
        })
    );
    
    // Clear diagnostics when document is closed
    context.subscriptions.push(
        vscode.workspace.onDidCloseTextDocument((document) => {
            if (document.languageId === 'clef') {
                diagnosticCollection.delete(document.uri);
            }
        })
    );
    
    outputChannel.appendLine('Clef extension activated');
}

function getPythonPath(): string {
    const config = vscode.workspace.getConfiguration('clef');
    return config.get('pythonPath', 'python');
}

function getSoundfontArg(): string[] {
    const config = vscode.workspace.getConfiguration('clef');
    const sfPath = config.get<string>('soundfontPath', '');
    if (sfPath) {
        return ['--soundfont', sfPath];
    }
    return [];
}

async function runScore() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'clef') {
        vscode.window.showErrorMessage('No Clef file is open');
        return;
    }
    
    // Save the document first
    await editor.document.save();
    
    const filePath = editor.document.fileName;
    const pythonPath = getPythonPath();
    const sfArgs = getSoundfontArg();
    
    outputChannel.clear();
    outputChannel.show();
    outputChannel.appendLine(`Running: ${filePath}`);
    outputChannel.appendLine('');
    
    const args = ['-m', 'clef', 'run', filePath, ...sfArgs];
    
    const process = cp.spawn(pythonPath, args, {
        cwd: path.dirname(filePath)
    });
    
    process.stdout.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.stderr.on('data', (data) => {
        outputChannel.append(data.toString());
    });
    
    process.on('close', (code) => {
        if (code === 0) {
            outputChannel.appendLine('\nPlayback complete');
        } else {
            outputChannel.appendLine(`\nProcess exited with code ${code}`);
        }
    });
}

async function validateScore() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'clef') {
        vscode.window.showErrorMessage('No Clef file is open');
        return;
    }
    
    await editor.document.save();
    validateDocument(editor.document);
}

function validateDocument(document: vscode.TextDocument) {
    const filePath = document.fileName;
    const pythonPath = getPythonPath();
    
    const args = ['-m', 'clef', 'validate', filePath, '--no-strict'];
    
    cp.exec(`"${pythonPath}" ${args.join(' ')}`, (error, stdout, stderr) => {
        const diagnostics: vscode.Diagnostic[] = [];
        
        if (error) {
            // Parse error output
            const output = stderr || stdout;
            const lines = output.split('\n');
            
            for (const line of lines) {
                // Try to parse error with line/column info
                const match = line.match(/at line (\d+)(?:, column (\d+))?/);
                if (match) {
                    const lineNum = parseInt(match[1], 10) - 1;
                    const colNum = match[2] ? parseInt(match[2], 10) - 1 : 0;
                    
                    const range = new vscode.Range(
                        new vscode.Position(lineNum, colNum),
                        new vscode.Position(lineNum, colNum + 10)
                    );
                    
                    const diagnostic = new vscode.Diagnostic(
                        range,
                        line,
                        vscode.DiagnosticSeverity.Error
                    );
                    diagnostics.push(diagnostic);
                }
            }
            
            if (diagnostics.length === 0 && output.trim()) {
                // Generic error at start of file
                const diagnostic = new vscode.Diagnostic(
                    new vscode.Range(0, 0, 0, 10),
                    output.trim(),
                    vscode.DiagnosticSeverity.Error
                );
                diagnostics.push(diagnostic);
            }
        } else {
            vscode.window.showInformationMessage('Clef: Validation passed!');
        }
        
        diagnosticCollection.set(document.uri, diagnostics);
    });
}

async function buildScore() {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'clef') {
        vscode.window.showErrorMessage('No Clef file is open');
        return;
    }
    
    await editor.document.save();
    
    const filePath = editor.document.fileName;
    const pythonPath = getPythonPath();
    
    // Ask for output format
    const format = await vscode.window.showQuickPick(['midi', 'wav'], {
        placeHolder: 'Select output format'
    });
    
    if (!format) {
        return;
    }
    
    outputChannel.clear();
    outputChannel.show();
    outputChannel.appendLine(`Building: ${filePath} to ${format.toUpperCase()}`);
    
    const args = ['-m', 'clef', 'build', filePath, '-f', format];
    
    cp.exec(`"${pythonPath}" ${args.join(' ')}`, {
        cwd: path.dirname(filePath)
    }, (error, stdout, stderr) => {
        if (error) {
            outputChannel.appendLine(`Error: ${stderr || error.message}`);
            vscode.window.showErrorMessage('Build failed');
        } else {
            outputChannel.appendLine(stdout);
            vscode.window.showInformationMessage(`Build complete: ${format.toUpperCase()}`);
        }
    });
}

export function deactivate() {
    if (outputChannel) {
        outputChannel.dispose();
    }
    if (diagnosticCollection) {
        diagnosticCollection.dispose();
    }
}

