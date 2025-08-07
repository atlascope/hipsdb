from django.db import models


class Image(models.Model):
    name: str = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class ROI(models.Model):
    name: str = models.CharField(max_length=255)
    image: Image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='rois')

    left: int = models.IntegerField()
    top: int = models.IntegerField()
    right: int = models.IntegerField()
    bottom: int = models.IntegerField()


class Nucleus(models.Model):
    roi: ROI = models.ForeignKey(ROI, on_delete=models.CASCADE, related_name="nuclei")

    Identifier_ObjectCode = models.IntegerField(db_column="Identifier.ObjectCode")
    Identifier_Xmin = models.IntegerField(db_column="Identifier.Xmin")
    Identifier_Ymin = models.IntegerField(db_column="Identifier.Ymin")
    Identifier_Xmax = models.IntegerField(db_column="Identifier.Xmax")
    Identifier_Ymax = models.IntegerField(db_column="Identifier.Ymax")
    Identifier_CentroidX = models.IntegerField(db_column="Identifier.CentroidX")
    Identifier_CentroidY = models.IntegerField(db_column="Identifier.CentroidY")
    Classif_StandardClass = models.CharField(
        max_length=22,
        choices=[
            ("ActiveStromalCellNOS", "ActiveStromalCellNOS"),
            ("ActiveTILsCell", "ActiveTILsCell"),
            ("BACKGROUND", "BACKGROUND"),
            ("CancerEpithelium", "CancerEpithelium"),
            ("NormalEpithelium", "NormalEpithelium"),
            ("OtherCell", "OtherCell"),
            ("StromalCellNOS", "StromalCellNOS"),
            ("TILsCell", "TILsCell"),
            ("UnknownOrAmbiguousCell", "UnknownOrAmbiguousCell"),
        ],
        db_column="Classif.StandardClass",
    )
    Classif_SuperClass = models.CharField(
        max_length=20,
        choices=[
            ("AmbiguousSuperclass", "AmbiguousSuperclass"),
            ("BACKGROUND", "BACKGROUND"),
            ("EpithelialSuperclass", "EpithelialSuperclass"),
            ("OtherSuperclass", "OtherSuperclass"),
            ("StromalSuperclass", "StromalSuperclass"),
            ("TILsSuperclass", "TILsSuperclass"),
        ],
        db_column="Classif.SuperClass",
    )
    ClassifProbab_CancerEpithelium = models.FloatField(
        db_column="ClassifProbab.CancerEpithelium"
    )
    ClassifProbab_StromalCellNOS = models.FloatField(
        db_column="ClassifProbab.StromalCellNOS"
    )
    ClassifProbab_ActiveStromalCellNOS = models.FloatField(
        db_column="ClassifProbab.ActiveStromalCellNOS"
    )
    ClassifProbab_TILsCell = models.FloatField(db_column="ClassifProbab.TILsCell")
    ClassifProbab_ActiveTILsCell = models.FloatField(
        db_column="ClassifProbab.ActiveTILsCell"
    )
    ClassifProbab_NormalEpithelium = models.FloatField(
        db_column="ClassifProbab.NormalEpithelium"
    )
    ClassifProbab_OtherCell = models.FloatField(db_column="ClassifProbab.OtherCell")
    ClassifProbab_UnknownOrAmbiguousCell = models.FloatField(
        db_column="ClassifProbab.UnknownOrAmbiguousCell"
    )
    ClassifProbab_BACKGROUND = models.FloatField(db_column="ClassifProbab.BACKGROUND")
    SuperClassifProbab_EpithelialSuperclass = models.FloatField(
        db_column="SuperClassifProbab.EpithelialSuperclass"
    )
    SuperClassifProbab_StromalSuperclass = models.FloatField(
        db_column="SuperClassifProbab.StromalSuperclass"
    )
    SuperClassifProbab_TILsSuperclass = models.FloatField(
        db_column="SuperClassifProbab.TILsSuperclass"
    )
    SuperClassifProbab_OtherSuperclass = models.FloatField(
        db_column="SuperClassifProbab.OtherSuperclass"
    )
    SuperClassifProbab_AmbiguousSuperclass = models.FloatField(
        db_column="SuperClassifProbab.AmbiguousSuperclass"
    )
    SuperClassifProbab_BACKGROUND = models.FloatField(
        db_column="SuperClassifProbab.BACKGROUND"
    )
    Unconstrained_Identifier_Xmin = models.IntegerField(
        db_column="Unconstrained.Identifier.Xmin"
    )
    Unconstrained_Identifier_Ymin = models.IntegerField(
        db_column="Unconstrained.Identifier.Ymin"
    )
    Unconstrained_Identifier_Xmax = models.IntegerField(
        db_column="Unconstrained.Identifier.Xmax"
    )
    Unconstrained_Identifier_Ymax = models.IntegerField(
        db_column="Unconstrained.Identifier.Ymax"
    )
    Unconstrained_Identifier_CentroidX = models.IntegerField(
        db_column="Unconstrained.Identifier.CentroidX"
    )
    Unconstrained_Identifier_CentroidY = models.IntegerField(
        db_column="Unconstrained.Identifier.CentroidY"
    )
    Unconstrained_Classif_StandardClass = models.CharField(
        max_length=22,
        choices=[
            ("ActiveStromalCellNOS", "ActiveStromalCellNOS"),
            ("ActiveTILsCell", "ActiveTILsCell"),
            ("BACKGROUND", "BACKGROUND"),
            ("CancerEpithelium", "CancerEpithelium"),
            ("NormalEpithelium", "NormalEpithelium"),
            ("StromalCellNOS", "StromalCellNOS"),
            ("TILsCell", "TILsCell"),
            ("UnknownOrAmbiguousCell", "UnknownOrAmbiguousCell"),
        ],
        db_column="Unconstrained.Classif.StandardClass",
    )
    Unconstrained_Classif_SuperClass = models.CharField(
        max_length=20,
        choices=[
            ("AmbiguousSuperclass", "AmbiguousSuperclass"),
            ("BACKGROUND", "BACKGROUND"),
            ("EpithelialSuperclass", "EpithelialSuperclass"),
            ("StromalSuperclass", "StromalSuperclass"),
            ("TILsSuperclass", "TILsSuperclass"),
        ],
        db_column="Unconstrained.Classif.SuperClass",
    )
    Unconstrained_ClassifProbab_CancerEpithelium = models.FloatField(
        db_column="Unconstrained.ClassifProbab.CancerEpithelium"
    )
    Unconstrained_ClassifProbab_StromalCellNOS = models.FloatField(
        db_column="Unconstrained.ClassifProbab.StromalCellNOS"
    )
    Unconstrained_ClassifProbab_ActiveStromalCellNOS = models.FloatField(
        db_column="Unconstrained.ClassifProbab.ActiveStromalCellNOS"
    )
    Unconstrained_ClassifProbab_TILsCell = models.FloatField(
        db_column="Unconstrained.ClassifProbab.TILsCell"
    )
    Unconstrained_ClassifProbab_ActiveTILsCell = models.FloatField(
        db_column="Unconstrained.ClassifProbab.ActiveTILsCell"
    )
    Unconstrained_ClassifProbab_NormalEpithelium = models.FloatField(
        db_column="Unconstrained.ClassifProbab.NormalEpithelium"
    )
    Unconstrained_ClassifProbab_OtherCell = models.FloatField(
        db_column="Unconstrained.ClassifProbab.OtherCell"
    )
    Unconstrained_ClassifProbab_UnknownOrAmbiguousCell = models.FloatField(
        db_column="Unconstrained.ClassifProbab.UnknownOrAmbiguousCell"
    )
    Unconstrained_ClassifProbab_BACKGROUND = models.FloatField(
        db_column="Unconstrained.ClassifProbab.BACKGROUND"
    )
    Unconstrained_SuperClassifProbab_EpithelialSuperclass = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.EpithelialSuperclass"
    )
    Unconstrained_SuperClassifProbab_StromalSuperclass = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.StromalSuperclass"
    )
    Unconstrained_SuperClassifProbab_TILsSuperclass = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.TILsSuperclass"
    )
    Unconstrained_SuperClassifProbab_OtherSuperclass = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.OtherSuperclass"
    )
    Unconstrained_SuperClassifProbab_AmbiguousSuperclass = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.AmbiguousSuperclass"
    )
    Unconstrained_SuperClassifProbab_BACKGROUND = models.FloatField(
        db_column="Unconstrained.SuperClassifProbab.BACKGROUND"
    )
    Identifier_WeightedCentroidX = models.FloatField(
        db_column="Identifier.WeightedCentroidX"
    )
    Identifier_WeightedCentroidY = models.FloatField(
        db_column="Identifier.WeightedCentroidY"
    )
    Orientation_Orientation = models.FloatField(db_column="Orientation.Orientation")
    Size_Area = models.IntegerField(db_column="Size.Area")
    Size_ConvexHullArea = models.IntegerField(db_column="Size.ConvexHullArea")
    Size_MajorAxisLength = models.FloatField(db_column="Size.MajorAxisLength")
    Size_MinorAxisLength = models.FloatField(db_column="Size.MinorAxisLength")
    Size_Perimeter = models.FloatField(db_column="Size.Perimeter")
    Shape_Circularity = models.FloatField(db_column="Shape.Circularity")
    Shape_Eccentricity = models.FloatField(db_column="Shape.Eccentricity")
    Shape_EquivalentDiameter = models.FloatField(db_column="Shape.EquivalentDiameter")
    Shape_Extent = models.FloatField(db_column="Shape.Extent")
    Shape_FractalDimension = models.FloatField(db_column="Shape.FractalDimension")
    Shape_MinorMajorAxisRatio = models.FloatField(db_column="Shape.MinorMajorAxisRatio")
    Shape_Solidity = models.FloatField(db_column="Shape.Solidity")
    Shape_HuMoments1 = models.FloatField(db_column="Shape.HuMoments1")
    Shape_HuMoments2 = models.FloatField(db_column="Shape.HuMoments2")
    Shape_HuMoments3 = models.FloatField(db_column="Shape.HuMoments3")
    Shape_HuMoments4 = models.FloatField(db_column="Shape.HuMoments4")
    Shape_HuMoments5 = models.FloatField(db_column="Shape.HuMoments5")
    Shape_HuMoments6 = models.FloatField(db_column="Shape.HuMoments6")
    Shape_HuMoments7 = models.FloatField(db_column="Shape.HuMoments7")
    Shape_WeightedHuMoments1 = models.FloatField(db_column="Shape.WeightedHuMoments1")
    Shape_WeightedHuMoments2 = models.FloatField(db_column="Shape.WeightedHuMoments2")
    Shape_WeightedHuMoments3 = models.FloatField(db_column="Shape.WeightedHuMoments3")
    Shape_WeightedHuMoments4 = models.FloatField(db_column="Shape.WeightedHuMoments4")
    Shape_WeightedHuMoments5 = models.FloatField(db_column="Shape.WeightedHuMoments5")
    Shape_WeightedHuMoments6 = models.FloatField(db_column="Shape.WeightedHuMoments6")
    Shape_WeightedHuMoments7 = models.FloatField(db_column="Shape.WeightedHuMoments7")
    Shape_FSD1 = models.FloatField(db_column="Shape.FSD1")
    Shape_FSD2 = models.FloatField(db_column="Shape.FSD2")
    Shape_FSD3 = models.FloatField(db_column="Shape.FSD3")
    Shape_FSD4 = models.FloatField(db_column="Shape.FSD4")
    Shape_FSD5 = models.FloatField(db_column="Shape.FSD5")
    Shape_FSD6 = models.FloatField(db_column="Shape.FSD6")
    Nucleus_Intensity_Min = models.IntegerField(db_column="Nucleus.Intensity.Min")
    Nucleus_Intensity_Max = models.IntegerField(db_column="Nucleus.Intensity.Max")
    Nucleus_Intensity_Mean = models.FloatField(db_column="Nucleus.Intensity.Mean")
    Nucleus_Intensity_Median = models.FloatField(db_column="Nucleus.Intensity.Median")
    Nucleus_Intensity_MeanMedianDiff = models.FloatField(
        db_column="Nucleus.Intensity.MeanMedianDiff"
    )
    Nucleus_Intensity_Std = models.FloatField(db_column="Nucleus.Intensity.Std")
    Nucleus_Intensity_IQR = models.FloatField(db_column="Nucleus.Intensity.IQR")
    Nucleus_Intensity_MAD = models.FloatField(db_column="Nucleus.Intensity.MAD")
    Nucleus_Intensity_Skewness = models.FloatField(
        db_column="Nucleus.Intensity.Skewness"
    )
    Nucleus_Intensity_Kurtosis = models.FloatField(
        db_column="Nucleus.Intensity.Kurtosis"
    )
    Nucleus_Intensity_HistEnergy = models.FloatField(
        db_column="Nucleus.Intensity.HistEnergy"
    )
    Nucleus_Intensity_HistEntropy = models.FloatField(
        db_column="Nucleus.Intensity.HistEntropy"
    )
    Cytoplasm_Intensity_Min = models.IntegerField(db_column="Cytoplasm.Intensity.Min")
    Cytoplasm_Intensity_Max = models.IntegerField(db_column="Cytoplasm.Intensity.Max")
    Cytoplasm_Intensity_Mean = models.FloatField(db_column="Cytoplasm.Intensity.Mean")
    Cytoplasm_Intensity_Median = models.FloatField(
        db_column="Cytoplasm.Intensity.Median"
    )
    Cytoplasm_Intensity_MeanMedianDiff = models.FloatField(
        db_column="Cytoplasm.Intensity.MeanMedianDiff"
    )
    Cytoplasm_Intensity_Std = models.FloatField(db_column="Cytoplasm.Intensity.Std")
    Cytoplasm_Intensity_IQR = models.FloatField(db_column="Cytoplasm.Intensity.IQR")
    Cytoplasm_Intensity_MAD = models.FloatField(db_column="Cytoplasm.Intensity.MAD")
    Cytoplasm_Intensity_Skewness = models.FloatField(
        db_column="Cytoplasm.Intensity.Skewness"
    )
    Cytoplasm_Intensity_Kurtosis = models.FloatField(
        db_column="Cytoplasm.Intensity.Kurtosis"
    )
    Cytoplasm_Intensity_HistEnergy = models.FloatField(
        db_column="Cytoplasm.Intensity.HistEnergy"
    )
    Cytoplasm_Intensity_HistEntropy = models.FloatField(
        db_column="Cytoplasm.Intensity.HistEntropy"
    )
    Nucleus_Gradient_Mag_Mean = models.FloatField(db_column="Nucleus.Gradient.Mag.Mean")
    Nucleus_Gradient_Mag_Std = models.FloatField(db_column="Nucleus.Gradient.Mag.Std")
    Nucleus_Gradient_Mag_Skewness = models.FloatField(
        db_column="Nucleus.Gradient.Mag.Skewness"
    )
    Nucleus_Gradient_Mag_Kurtosis = models.FloatField(
        db_column="Nucleus.Gradient.Mag.Kurtosis"
    )
    Nucleus_Gradient_Mag_HistEntropy = models.FloatField(
        db_column="Nucleus.Gradient.Mag.HistEntropy"
    )
    Nucleus_Gradient_Mag_HistEnergy = models.FloatField(
        db_column="Nucleus.Gradient.Mag.HistEnergy"
    )
    Nucleus_Gradient_Canny_Sum = models.IntegerField(
        db_column="Nucleus.Gradient.Canny.Sum"
    )
    Nucleus_Gradient_Canny_Mean = models.FloatField(
        db_column="Nucleus.Gradient.Canny.Mean"
    )
    Cytoplasm_Gradient_Mag_Mean = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.Mean"
    )
    Cytoplasm_Gradient_Mag_Std = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.Std"
    )
    Cytoplasm_Gradient_Mag_Skewness = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.Skewness"
    )
    Cytoplasm_Gradient_Mag_Kurtosis = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.Kurtosis"
    )
    Cytoplasm_Gradient_Mag_HistEntropy = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.HistEntropy"
    )
    Cytoplasm_Gradient_Mag_HistEnergy = models.FloatField(
        db_column="Cytoplasm.Gradient.Mag.HistEnergy"
    )
    Cytoplasm_Gradient_Canny_Sum = models.IntegerField(
        db_column="Cytoplasm.Gradient.Canny.Sum"
    )
    Cytoplasm_Gradient_Canny_Mean = models.FloatField(
        db_column="Cytoplasm.Gradient.Canny.Mean"
    )
    Nucleus_Haralick_ASM_Mean = models.FloatField(db_column="Nucleus.Haralick.ASM.Mean")
    Nucleus_Haralick_ASM_Range = models.FloatField(
        db_column="Nucleus.Haralick.ASM.Range"
    )
    Nucleus_Haralick_Contrast_Mean = models.FloatField(
        db_column="Nucleus.Haralick.Contrast.Mean"
    )
    Nucleus_Haralick_Contrast_Range = models.FloatField(
        db_column="Nucleus.Haralick.Contrast.Range"
    )
    Nucleus_Haralick_Correlation_Mean = models.FloatField(
        db_column="Nucleus.Haralick.Correlation.Mean"
    )
    Nucleus_Haralick_Correlation_Range = models.FloatField(
        db_column="Nucleus.Haralick.Correlation.Range"
    )
    Nucleus_Haralick_SumOfSquares_Mean = models.FloatField(
        db_column="Nucleus.Haralick.SumOfSquares.Mean"
    )
    Nucleus_Haralick_SumOfSquares_Range = models.FloatField(
        db_column="Nucleus.Haralick.SumOfSquares.Range"
    )
    Nucleus_Haralick_IDM_Mean = models.FloatField(db_column="Nucleus.Haralick.IDM.Mean")
    Nucleus_Haralick_IDM_Range = models.FloatField(
        db_column="Nucleus.Haralick.IDM.Range"
    )
    Nucleus_Haralick_SumAverage_Mean = models.FloatField(
        db_column="Nucleus.Haralick.SumAverage.Mean"
    )
    Nucleus_Haralick_SumAverage_Range = models.FloatField(
        db_column="Nucleus.Haralick.SumAverage.Range"
    )
    Nucleus_Haralick_SumVariance_Mean = models.FloatField(
        db_column="Nucleus.Haralick.SumVariance.Mean"
    )
    Nucleus_Haralick_SumVariance_Range = models.FloatField(
        db_column="Nucleus.Haralick.SumVariance.Range"
    )
    Nucleus_Haralick_SumEntropy_Mean = models.FloatField(
        db_column="Nucleus.Haralick.SumEntropy.Mean"
    )
    Nucleus_Haralick_SumEntropy_Range = models.FloatField(
        db_column="Nucleus.Haralick.SumEntropy.Range"
    )
    Nucleus_Haralick_Entropy_Mean = models.FloatField(
        db_column="Nucleus.Haralick.Entropy.Mean"
    )
    Nucleus_Haralick_Entropy_Range = models.FloatField(
        db_column="Nucleus.Haralick.Entropy.Range"
    )
    Nucleus_Haralick_DifferenceVariance_Mean = models.FloatField(
        db_column="Nucleus.Haralick.DifferenceVariance.Mean"
    )
    Nucleus_Haralick_DifferenceVariance_Range = models.FloatField(
        db_column="Nucleus.Haralick.DifferenceVariance.Range"
    )
    Nucleus_Haralick_DifferenceEntropy_Mean = models.FloatField(
        db_column="Nucleus.Haralick.DifferenceEntropy.Mean"
    )
    Nucleus_Haralick_DifferenceEntropy_Range = models.FloatField(
        db_column="Nucleus.Haralick.DifferenceEntropy.Range"
    )
    Nucleus_Haralick_IMC1_Mean = models.FloatField(
        db_column="Nucleus.Haralick.IMC1.Mean"
    )
    Nucleus_Haralick_IMC1_Range = models.FloatField(
        db_column="Nucleus.Haralick.IMC1.Range"
    )
    Nucleus_Haralick_IMC2_Mean = models.FloatField(
        db_column="Nucleus.Haralick.IMC2.Mean"
    )
    Nucleus_Haralick_IMC2_Range = models.FloatField(
        db_column="Nucleus.Haralick.IMC2.Range"
    )
    Cytoplasm_Haralick_ASM_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.ASM.Mean"
    )
    Cytoplasm_Haralick_ASM_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.ASM.Range"
    )
    Cytoplasm_Haralick_Contrast_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.Contrast.Mean"
    )
    Cytoplasm_Haralick_Contrast_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.Contrast.Range"
    )
    Cytoplasm_Haralick_Correlation_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.Correlation.Mean"
    )
    Cytoplasm_Haralick_Correlation_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.Correlation.Range"
    )
    Cytoplasm_Haralick_SumOfSquares_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.SumOfSquares.Mean"
    )
    Cytoplasm_Haralick_SumOfSquares_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.SumOfSquares.Range"
    )
    Cytoplasm_Haralick_IDM_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.IDM.Mean"
    )
    Cytoplasm_Haralick_IDM_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.IDM.Range"
    )
    Cytoplasm_Haralick_SumAverage_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.SumAverage.Mean"
    )
    Cytoplasm_Haralick_SumAverage_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.SumAverage.Range"
    )
    Cytoplasm_Haralick_SumVariance_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.SumVariance.Mean"
    )
    Cytoplasm_Haralick_SumVariance_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.SumVariance.Range"
    )
    Cytoplasm_Haralick_SumEntropy_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.SumEntropy.Mean"
    )
    Cytoplasm_Haralick_SumEntropy_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.SumEntropy.Range"
    )
    Cytoplasm_Haralick_Entropy_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.Entropy.Mean"
    )
    Cytoplasm_Haralick_Entropy_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.Entropy.Range"
    )
    Cytoplasm_Haralick_DifferenceVariance_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.DifferenceVariance.Mean"
    )
    Cytoplasm_Haralick_DifferenceVariance_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.DifferenceVariance.Range"
    )
    Cytoplasm_Haralick_DifferenceEntropy_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.DifferenceEntropy.Mean"
    )
    Cytoplasm_Haralick_DifferenceEntropy_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.DifferenceEntropy.Range"
    )
    Cytoplasm_Haralick_IMC1_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.IMC1.Mean"
    )
    Cytoplasm_Haralick_IMC1_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.IMC1.Range"
    )
    Cytoplasm_Haralick_IMC2_Mean = models.FloatField(
        db_column="Cytoplasm.Haralick.IMC2.Mean"
    )
    Cytoplasm_Haralick_IMC2_Range = models.FloatField(
        db_column="Cytoplasm.Haralick.IMC2.Range"
    )
