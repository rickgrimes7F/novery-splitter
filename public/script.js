let okLines = [];
let nvLines = [];

async function startChecking() {
    let raw = document.getElementById("inputBox").value;

    document.getElementById("logsBox").value = "Starting...\n";

    okLines = [];
    nvLines = [];

    let response = await fetch("/api/split", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            data: raw
        })
    });

    let results = await response.json();

    let ok = 0;
    let nv = 0;

    for (let x of results) {

        if (x.status === "ok") {
            ok++;
            okLines.push(x.line);

            document.getElementById("logsBox").value +=
                `[OK] ${x.uid}\n`;
        }

        if (x.status === "nv") {
            nv++;
            nvLines.push(x.line);

            document.getElementById("logsBox").value +=
                `[NV] ${x.uid}\n`;
        }

        document.getElementById("okCounter").innerText =
            `OK: ${ok}`;

        document.getElementById("nvCounter").innerText =
            `NV: ${nv}`;
    }

    document.getElementById("logsBox").value +=
        "\nDone Checking.";
}


function copyOK() {
    navigator.clipboard.writeText(
        okLines.join("\n")
    );
    alert("OK copied");
}


function copyNV() {
    navigator.clipboard.writeText(
        nvLines.join("\n")
    );
    alert("NV copied");
}
