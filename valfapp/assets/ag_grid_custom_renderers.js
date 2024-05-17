const gridOptions = {
    components: {
        'sparklineCellRenderer': sparklineCellRenderer
    },
    // other grid options...
};

function sparklineCellRenderer(params) {
    const element = document.createElement('span');
    try {
        if (params.value && Array.isArray(params.value)) {
            Sparkline.draw(element, params.value);
        } else {
            element.textContent = 'No data';
        }
    } catch (error) {
        console.error("Failed to render sparkline:", error);
        element.textContent = 'Render error';
    }
    return element;
}


var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});


dagcomponentfuncs.Button = function (props) {
    const {setData, data} = props;

    function onClick() {
        setData();
    }
    return React.createElement(
        'button',
        {
            onClick: onClick,
            className: props.className,
        },
        props.value
    );
};

