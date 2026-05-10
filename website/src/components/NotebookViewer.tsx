import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface Output {
  output_type: "execute_result" | "stream" | "display_data" | "error";
  data?: { "text/plain"?: string[]; "text/html"?: string[] };
  text?: string[];
}

interface Cell {
  cell_type: "markdown" | "code" | "raw";
  source: string[];
  outputs?: Output[];
}

export interface NotebookData {
  cells: Cell[];
}

const MD_COMPONENTS = {
  h1: ({ children }: React.PropsWithChildren) => <h1 className="text-xl font-bold mt-6 mb-2 text-gray-900 dark:text-gray-100 first:mt-0">{children}</h1>,
  h2: ({ children }: React.PropsWithChildren) => <h2 className="text-base font-semibold mt-6 mb-1 text-gray-900 dark:text-gray-100">{children}</h2>,
  h3: ({ children }: React.PropsWithChildren) => <h3 className="text-sm font-semibold mt-4 mb-1 text-gray-900 dark:text-gray-100">{children}</h3>,
  p:  ({ children }: React.PropsWithChildren) => <p className="mb-2 text-sm">{children}</p>,
  ul: ({ children }: React.PropsWithChildren) => <ul className="list-disc list-outside ml-5 mb-2 space-y-0.5 text-sm">{children}</ul>,
  ol: ({ children }: React.PropsWithChildren) => <ol className="list-decimal list-outside ml-5 mb-2 space-y-0.5 text-sm">{children}</ol>,
  li: ({ children }: React.PropsWithChildren) => <li>{children}</li>,
  code: ({ children }: React.PropsWithChildren) => <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
  a:   ({ href, children }: React.PropsWithChildren<{ href?: string }>) => <a href={href} className="underline text-blue-600 dark:text-blue-400 hover:opacity-80" target="_blank" rel="noopener noreferrer">{children}</a>,
  blockquote: ({ children }: React.PropsWithChildren) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-3 italic text-gray-500 dark:text-gray-400 my-3">{children}</blockquote>,
};

function CellOutput({ output }: { output: Output }) {
  const html = output.data?.["text/html"]?.join("");
  if (html) {
    return (
      <div
        className="overflow-x-auto text-xs [&_table]:border-collapse [&_td]:border [&_td]:border-gray-300 [&_td]:dark:border-gray-600 [&_td]:px-2 [&_td]:py-0.5 [&_th]:border [&_th]:border-gray-300 [&_th]:dark:border-gray-600 [&_th]:px-2 [&_th]:py-0.5 [&_th]:bg-gray-100 [&_th]:dark:bg-gray-800"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  }

  const text = (output.data?.["text/plain"] ?? output.text ?? []).join("");
  if (!text) return null;
  return <pre className="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap break-all">{text}</pre>;
}

function CodeCell({ cell }: { cell: Cell }) {
  const [open, setOpen] = useState(false);
  const source = cell.source.join("");
  const outputs = cell.outputs ?? [];
  if (!source && outputs.length === 0) return null;

  return (
    <div className="rounded-md overflow-hidden border border-gray-200 dark:border-gray-700">
      {source && (
        <SyntaxHighlighter
          language="python"
          style={oneDark}
          customStyle={{ margin: 0, borderRadius: 0, fontSize: "0.75rem" }}
        >
          {source}
        </SyntaxHighlighter>
      )}
      {outputs.length > 0 && (
        <>
          <button
            onClick={() => setOpen((o) => !o)}
            className="w-full flex items-center gap-1.5 px-4 py-1.5 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 transition-colors"
          >
            <span className="text-[10px]">{open ? "▾" : "▸"}</span>
            {open ? "hide output" : "show output"}
          </button>
          {open && (
            <div className="px-4 py-2 bg-white dark:bg-gray-900 space-y-1 border-t border-gray-200 dark:border-gray-700">
              {outputs.map((o, j) => <CellOutput key={j} output={o} />)}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export function NotebookViewer({ notebook }: { notebook: NotebookData }) {
  return (
    <div className="space-y-4">
      {notebook.cells.map((cell, i) => {
        if (cell.cell_type === "markdown") {
          return (
            <div key={i}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                {cell.source.join("")}
              </ReactMarkdown>
            </div>
          );
        }
        if (cell.cell_type === "code") {
          return <CodeCell key={i} cell={cell} />;
        }
        return null;
      })}
    </div>
  );
}
