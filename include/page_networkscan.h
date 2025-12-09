#ifndef page_networkscan_h
#define page_networkscan_h

#include <QWidget>

QT_BEGIN_NAMESPACE
namespace Ui {
class page_networkscan;
}
QT_END_NAMESPACE

class page_networkscan : public QWidget
{
    Q_OBJECT

public:
    explicit page_networkscan(QWidget *parent = nullptr);
    ~page_networkscan();

private:
    Ui::page_networkscan *ui;
};

#endif // page_networkscan_h